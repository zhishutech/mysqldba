
CREATE VIEW revenue0 AS
SELECT
    l_suppkey AS supplier_no,
    sum(l_extendedprice * (1 - l_discount)) AS total_revenue
FROM lineitem
WHERE (l_shipdate >= toDate('1997-08-01')) AND (l_shipdate < (toDate('1997-08-01') + toIntervalMonth('3')))
GROUP BY l_suppkey;


select
	s_suppkey,
	s_name,
	s_address,
	s_phone,
	total_revenue
from
	supplier,
	revenue0
where
	s_suppkey = supplier_no
	and total_revenue = (
		select
			max(total_revenue)
		from
			revenue0
	)
order by
	s_suppkey;

drop view revenue0 ;



