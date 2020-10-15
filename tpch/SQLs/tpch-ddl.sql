
drop database tpch;
create database tpch default character set latin1;
use tpch;

-- sCCSID:     @(#)DSS.DDL	2.1.8.1
create table nation  ( n_nationkey  integer not null,
                            n_name       char(25) not null,
                            n_regionkey  integer not null,
                            n_comment    varchar(152));

create table region  ( r_regionkey  integer not null,
                            r_name       char(25) not null,
                            r_comment    varchar(152));

create table part  ( p_partkey     integer not null,
                          p_name        varchar(55) not null,
                          p_mfgr        char(25) not null,
                          p_brand       char(10) not null,
                          p_type        varchar(25) not null,
                          p_size        integer not null,
                          p_container   char(10) not null,
                          p_retailprice decimal(15,2) not null,
                          p_comment     varchar(23) not null );

create table supplier ( s_suppkey     integer not null,
                             s_name        char(25) not null,
                             s_address     varchar(40) not null,
                             s_nationkey   integer not null,
                             s_phone       char(15) not null,
                             s_acctbal     decimal(15,2) not null,
                             s_comment     varchar(101) not null);

create table partsupp ( ps_partkey     integer not null,
                             ps_suppkey     integer not null,
                             ps_availqty    integer not null,
                             ps_supplycost  decimal(15,2)  not null,
                             ps_comment     varchar(199) not null );

create table customer ( c_custkey     integer not null,
                             c_name        varchar(25) not null,
                             c_address     varchar(40) not null,
                             c_nationkey   integer not null,
                             c_phone       char(15) not null,
                             c_acctbal     decimal(15,2)   not null,
                             c_mktsegment  char(10) not null,
                             c_comment     varchar(117) not null);

create table orders  ( o_orderkey       integer not null,
                           o_custkey        integer not null,
                           o_orderstatus    char(1) not null,
                           o_totalprice     decimal(15,2) not null,
                           o_orderdate      date not null,
                           o_orderpriority  char(15) not null,  
                           o_clerk          char(15) not null, 
                           o_shippriority   integer not null,
                           o_comment        varchar(79) not null);

create table lineitem ( l_orderkey    integer not null,
                             l_partkey     integer not null,
                             l_suppkey     integer not null,
                             l_linenumber  integer not null,
                             l_quantity    decimal(15,2) not null,
                             l_extendedprice  decimal(15,2) not null,
                             l_discount    decimal(15,2) not null,
                             l_tax         decimal(15,2) not null,
                             l_returnflag  char(1) not null,
                             l_linestatus  char(1) not null,
                             l_shipdate    date not null,
                             l_commitdate  date not null,
                             l_receiptdate date not null,
                             l_shipinstruct char(25) not null,
                             l_shipmode     char(10) not null,
                             l_comment      varchar(44) not null);

-- sCCSID:     @(#)DSS.RI	2.1.8.1
-- tpch bENCHMARK vERSION 8.0

use tpch;

-- alter table tpch.region drop primary key;
-- alter table tpch.nation drop primary key;
-- alter table tpch.part drop primary key;
-- alter table tpch.supplier drop primary key;
-- alter table tpch.partsupp drop primary key;
-- alter table tpch.orders drop primary key;
-- alter table tpch.lineitem drop primary key;
-- alter table tpch.customer drop primary key;


-- fOR TABLE region
alter table tpch.region
add primary key (r_regionkey);

-- fOR TABLE nation
alter table tpch.nation
add primary key (n_nationkey);

commit work;

-- fOR TABLE part
alter table tpch.part
add primary key (p_partkey);

commit work;

-- fOR TABLE supplier
alter table tpch.supplier
add primary key (s_suppkey);

commit work;

-- fOR TABLE partsupp
alter table tpch.partsupp
add primary key (ps_partkey,ps_suppkey);

commit work;

-- fOR TABLE customer
alter table tpch.customer
add primary key (c_custkey);

commit work;

-- fOR TABLE lineitem
alter table tpch.lineitem
add primary key (l_orderkey,l_linenumber);

commit work;

-- fOR TABLE orders
alter table tpch.orders
add primary key (o_orderkey);

commit work;



alter table tpch.nation
add foreign key nation_fk1 (n_regionkey) REFERENCES tpch.region(R_REGIONKEY);

alter table tpch.supplier
add foreign key supplier_fk1 (s_nationkey) REFERENCES tpch.nation(N_NATIONKEY);


alter table tpch.customer
add foreign key customer_fk1 (c_nationkey) REFERENCES tpch.nation(N_NATIONKEY);

alter table tpch.partsupp
add foreign key partsupp_fk1 (ps_suppkey) REFERENCES tpch.supplier(S_SUPPKEY);

alter table tpch.partsupp
add foreign key partsupp_fk2 (ps_partkey) REFERENCES tpch.part(P_PARTKEY);

alter table tpch.orders
add foreign key orders_fk1 (o_custkey) REFERENCES tpch.customer(C_CUSTKEY);


alter table tpch.lineitem
add foreign key lineitem_fk1 (l_orderkey)  REFERENCES tpch.orders(O_ORDERKEY);

alter table tpch.lineitem
add foreign key lineitem_fk2 (l_partkey,l_suppkey) REFERENCES 
        tpch.partsupp(PS_PARTKEY,PS_SUPPKEY);

