PREFIX=/usr/local/test
CC = gcc
CFLAGS = -g -Wall -I/usr/local/include 
LDFLAGS = -L/usr/lib/mysql -lmysqlclient
MYSQL_OBJS = logmysqldb_daemon.o confparser.o
INSTALL = /usr/bin/install
CONF = db.cf

all : logmysqldb_daemon 

clean:
	rm -rf *.o logmysqldb_daemon 

logmysqldb_daemon: $(MYSQL_OBJS) define.h
	$(CC) $(CFLAGS) -o $@ logmysqldb_daemon.c confparser.c $(LDFLAGS) 

install:
	mkdir $(PREFIX) 
	$(INSTALL) -o nobody -g nobody -m 755 logmysqldb_daemon $(PREFIX)/logmysqldb_daemon
	$(INSTALL) -o nobody -g nobody -m 755 $(CONF) $(PREFIX)/$(CONF)

