--建表：lagou岗位维度表
use spider;
drop table if exists dim_lagou;

CREATE TABLE IF NOT EXISTS dim_lagou (
    id int(5) NOT NULL AUTO_INCREMENT,
	job_type varchar(255) DEFAULT NULL COMMENT '职位',
    job_base_url varchar(255) DEFAULT NULL COMMENT '主页url',
    max_page_num int(5) DEFAULT NULL COMMENT '最大页数',
    PRIMARY KEY (job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

select * from dim_lagou;


--建表：lagou岗位信息表
create database if not exists spider;
use spider;
drop table if exists lagou;

CREATE TABLE IF NOT EXISTS lagou (
    id int(11) NOT NULL AUTO_INCREMENT,
    t_job varchar(255) DEFAULT NULL COMMENT '职位',
    t_addr varchar(255) DEFAULT NULL COMMENT '企业地址',
    t_com varchar(255) DEFAULT NULL COMMENT '企业名称',
    t_tag varchar(255) DEFAULT NULL COMMENT '企业标签',
    t_money varchar(255) DEFAULT NULL COMMENT '薪资待遇',
    t_edu varchar(255) DEFAULT NULL COMMENT '学历要求',
    t_exp varchar(255) DEFAULT NULL COMMENT '工作经验要求',
    t_type varchar(255) DEFAULT NULL COMMENT '企业类型',
    t_level varchar(255) DEFAULT NULL COMMENT '企业融资情况',
    t_csize varchar(255) DEFAULT NULL COMMENT '企业规模',
    t_benefit varchar(255) DEFAULT NULL COMMENT '福利待遇',
    t_pubdate varchar(255) DEFAULT NULL COMMENT '发布时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

show tabls;
select * from lagou;

--建表：已抓取网页地址表
use spider;
drop table if exists lagou_page_fetched;

CREATE TABLE IF NOT EXISTS lagou_page_fetched (
		id int(5)  NOT NULL AUTO_INCREMENT,
    job_id int(5) DEFAULT NULL COMMENT '职位大类id',
		page_url varchar(255) DEFAULT NULL COMMENT '职位具体url',
    is_fetched int(1) DEFAULT NULL COMMENT '是否已抓取完毕',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

select * from lagou_page_fetched;
