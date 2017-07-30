#!/usr/bin/ruby
#
# Author: Libing Song(宋利兵)
# Wixin Official Accounts: mysqlcode
# 分析InnoDB数据文件中B+Tree数据结构脚本
# 相关阅读：
# 

class IBD_page
  PAGE_SIZE = 16 * 1024

  @@INVALID_PAGE_NO = 0xFFFFFFFF

  @@FIL_PAGE_SPACE_OR_CHKSUM = 0
  @@FIL_PAGE_OFFSET = 4
  @@FIL_PAGE_PREV = 8
  @@FIL_PAGE_NEXT = 12
  @@FIL_PAGE_LSN = 16
  @@FIL_PAGE_TYPE = 24

  # Page type of index
  @@FIL_PAGE_INDEX = 17855

  # Offset of the data on the page
  @@FIL_PAGE_DATA = 38

  # On a page of any file segment, data may be put starting from this offset
  @@FSEG_PAGE_DATA = @@FIL_PAGE_DATA
  @@FSEG_HEADER_SIZE = 10

  # Offset of page header
  @@PAGE_HEADER = @@FIL_PAGE_DATA
  # Offset of data on the page
  @@PAGE_DATA = @@PAGE_HEADER + 36 + 2 * @@FSEG_HEADER_SIZE

  # Records in the page
  @@PAGE_N_RECS = 16
  #Level of the node in the index tree; the leaf level is the level 0 */
  @@PAGE_LEVEL = 26

  @@REC_N_NEW_EXTRA_BYTES = 5
  @@PAGE_NEW_INFIMUM = @@PAGE_DATA + @@REC_N_NEW_EXTRA_BYTES
  @@PAGE_NEW_SUPREMUM = @@PAGE_DATA + 2 * @@REC_N_NEW_EXTRA_BYTES + 8

  @@REC_NEXT = 2
  @@REC_NEW_INFO_BITS = 5
  @@REC_INFO_BITS_MASK = 0xF0
  @@REC_INFO_MIN_REC_FLAG = 0x10
  @@REC_INFO_DELETED_FLAG = 0x20

  def initialize(buf, page_no)
    @buf = buf
    @page_no = page_no
  end

  def type
    get_int2(@@FIL_PAGE_TYPE)
  end

  def in_btr()
    type() == @@FIL_PAGE_INDEX
  end

  def is_btr_root()
    in_btr() and prev_page() == @@INVALID_PAGE_NO and next_page() == @@INVALID_PAGE_NO
  end

  def level
    get_int2(@@PAGE_HEADER + @@PAGE_LEVEL)
  end

  def record_count
    get_int2(@@PAGE_HEADER + @@PAGE_N_RECS)
  end

  def prev_page()
    get_int4(@@FIL_PAGE_PREV)
  end

  def next_page()
    get_int4(@@FIL_PAGE_NEXT)
  end

  def first_rec()
    next_rec(@@PAGE_NEW_INFIMUM)
  end

  def next_rec(rec)
    # The offset of next record is against to current record's position
    offset = get_int2(rec - @@REC_NEXT) + rec
    offset = (offset + PAGE_SIZE * @page_no) & (PAGE_SIZE - 1)

    if offset == @@PAGE_NEW_SUPREMUM
      offset = 0
    end
    return offset
  end

  def rec_key_str(rec, len)
    get_str(rec, len)
  end

  def rec_pointer(rec, key_len)
    if level == 0
      return 0
    else
      # Pointer is the last field of index row
      get_int4(rec+key_len)
    end
  end

  def rec_flags(rec)
    flag = get_int1(rec - @@REC_NEW_INFO_BITS)
    str=""
    if flag & @@REC_INFO_DELETED_FLAG == @@REC_INFO_DELETED_FLAG
      str = "D"
    end
    if flag & @@REC_INFO_MIN_REC_FLAG == @@REC_INFO_MIN_REC_FLAG
      str = str + "M"
    end
    str
  end

  # Get a 1 byte number from page buffer
  def get_int1(offset)
    @buf[offset]
  end

  # Get a 2 byte number from page buffer
  def get_int2(offset)
    s = @buf[offset..offset+2]
    s = s.unpack("n")
    s.to_s.to_i
  end

  # Get a 4 byte number from page buffer
  def get_int4(offset)
    s = @buf[offset..offset+4]
    s = s.unpack("N")
    s.to_s.to_i
  end

  # Get a 'len' long string from page buffer
  def get_str(offset, len)
    @buf[offset..offset+len-1]
  end
end

class IBD_file
  def initialize(filename)
    @size = File.size?(filename)
    @file = File.new(filename, "r")
  end

  def read_page(page_no)
    if (page_no * IBD_page::PAGE_SIZE > @size)
      printf("Page No.(%d) is too large", page_no)
      return nil
    end

    @file.pos = page_no * IBD_page::PAGE_SIZE
    IBD_page.new(@file.read(IBD_page::PAGE_SIZE), page_no)
  end

  def page_count
    @size / IBD_page::PAGE_SIZE
  end

  def btr_roots()
    a = []
    page_count().times do |i|
      page = read_page(i)
      if page.is_btr_root()
        a = a + [i]
      end
    end
    return a
  end

  def print_btr_roots(print_key_len)
    btr_roots.each do |page_no|
      page = read_page(page_no)

      printf("B-Tree Root Page: %d, Level: %d, Records: %d\n", page_no.to_s,
             page.level, page.record_count)

      rec = page.first_rec
      while rec != 0
        printf(" Key(%s)\n", page.rec_key_str(rec, print_key_len))
        rec = page.next_rec(rec)
      end
    end
  end

  def print_btr(root, key_len, print_key_len)
    page_no = root
    next_level_page_no = -1
    while page_no > 0
      page = read_page(page_no)
      if (!page)
        puts "Reading page failed. You probable set a wrong key length"
        exit 1
      end

      printf("Page: %d, Level: %d, Records: %d\n", page_no.to_s, page.level,
             page.record_count)

      rec = page.first_rec
      while rec != 0
        if page.level == 0
          printf("  Flags(%s), Key(%s)\n", page.rec_flags(rec),
                 page.rec_key_str(rec, print_key_len))
        else
          printf("  Flags(%s), Key(%s), Pointer(%d)\n", page.rec_flags(rec),
                 page.rec_key_str(rec, print_key_len),
                 page.rec_pointer(rec, key_len))
        end

        if next_level_page_no == -1
          next_level_page_no = page.rec_pointer(rec, key_len)
        end
        rec = page.next_rec(rec)
      end

      page_no = page.next_page
      if page_no == 0xFFFFFFFF
        page_no = next_level_page_no
        next_level_page_no = -1
      end # if
    end # while
  end # def

end

def print_help()
  puts <<-EOF
ibd-analizer useage:
./ibd-analizer.rb [OPTIONS] <ibdfile>
OPTIONS
=======
-h, --help:
  show help.
-R, --roots:
  print all root pages of b-trees.
-r n, --root-page n:
  print the b-tree that starts at 'n' page. it will be ignored if '-R' is set.
-L n, --key-len n:
  the key of the b-tree is 'n' bytes long. It has to be set with '-r' together.
  In a clustered index b-tree, it is the sum of all primary key fields(length).
  In a secondary index b-tree, it is the sum of all the secondary key fields and
  primary key fields. E.g.
    CREATE TABLE t1(c1 char(4) PRIMARY KEY, c2 char(5), INDEX(c2));
    In clustered index b-tree, the key length is 4.
    In secondary index b-tree, the key length is 9.
-l n, --print-key-len n:
  print only the first 'n' bytes of the key. The first 4 bytes will be printed,
  if it is not set.
OUTPUT FIELDS
=============
Page
  Page No. of current page.
Level
  B-Tree level of current page.
Records
   How many records(include deleted records) in the page.
Flags
  M - It is the minimum key record in the same level of the b-tree.
  D - The record was marked as 'deleted'. It has been delete by user.
Key
  Value of the key.
Pointer
  Page No. of the next level page belongs to the key.
  EOF
end

require 'getoptlong'

def main
  roots = nil
  root_page = nil
  key_len = nil
  print_key_len = 4 # Print only the first 4 bytes of keys, by default

  opts = GetoptLong.new(
    ['--help', '-h', GetoptLong::NO_ARGUMENT],
    ['--roots', '-R', GetoptLong::NO_ARGUMENT],
    ['--root-page', '-r', GetoptLong::REQUIRED_ARGUMENT],
    ['--key-len', '-L', GetoptLong::REQUIRED_ARGUMENT],
    ['--print-key-len', '-l', GetoptLong::REQUIRED_ARGUMENT]
  )

  opts.each do |opt, arg|
    case opt
    when '--help'
      print_help
    when '--roots'
      root = true
    when '--root-page'
      root_page = arg.to_i
    when '--key-len'
      key_len = arg.to_i()
    when '--print-key-len'
      print_key_len = arg.to_i
    end
  end

  if ARGV.length != 1
    puts "Missing ibdfile argument!"
    print_help
    exit 0
  end

  f = IBD_file.new(ARGV.shift)
  if roots or !root_page
    f.print_btr_roots(print_key_len)
  else
    if !key_len
      puts "--key-len is not set. It has to be set when you print a b-tree."
      exit 1
    end
    f.print_btr(root_page, key_len, print_key_len)
  end
end

main
