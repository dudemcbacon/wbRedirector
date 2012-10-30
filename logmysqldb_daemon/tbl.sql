CREATE TABLE access_log(
     timestamp     DECIMAL(15,3),
     resp_time     INTEGER,
     src_ip        CHAR(15),
     cache_status  VARCHAR(20),
     http_status   VARCHAR(10),
     reply_size    INTEGER,
     req_method    VARCHAR(20),
     req_uri       VARCHAR(1000),
     username      VARCHAR(20),
     peer_access   VARCHAR(20),
     dst_ip        CHAR(15),
     mime_type     VARCHAR(50)
);
GRANT SELECT,INSERT,UPDATE,DELETE ON access_log TO squid@localhost IDENTIFIED BY 'squid';

