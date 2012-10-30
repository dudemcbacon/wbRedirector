/* logmysqldb_daemon.c - This file reads the access info from squid on stdin and logs to mysql database
 * (C) 2008 ViSolve Inc..
 * Released under GPL V2 
 */

/* Sending info to stdout would increase squid buffers so supress them all other 
 * than for trouble-shooting by "undef LDM_DEBUG".
 */

#undef LDM_DEBUG
//#define LDM_DEBUG 1

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <assert.h>
#include <sys/param.h>
#include <sys/stat.h>
#include <signal.h>
#include <errno.h>
#include <string.h>
#include <paths.h>
#include <mysql/mysql.h>
#include <syslog.h>
#include <stdarg.h>
#include "define.h"

#define COLUMN_COUNT 12
/* parse buffer - ie, length of longest expected line */
#define	LOGFILE_BUF_LEN		65536

extern int parse (char *, struct dbconf *);

static int
db_connect(MYSQL * myconn, struct dbconf dbcf) {
    my_bool reconnect = 1;

    mysql_init (myconn);
    if (myconn == NULL) {
        syslog (LOG_WARNING, "Error: initializing MYSQL structure");
        return (1);
    }

#ifdef LDM_DEBUG
    fprintf (stdout, " host:%s\n user:%s\n passwd:%s\n dbname:%s\n\n",
        dbcf.db_hostname, dbcf.db_username,
        dbcf.db_password, dbcf.db_dbname);
#endif
    if ((mysql_real_connect (myconn, dbcf.db_hostname, dbcf.db_username,
       dbcf.db_password, dbcf.db_dbname, 0, NULL, 0)) == NULL ) {
        syslog (LOG_WARNING, "Error %d:  %s.\n", mysql_errno (myconn), mysql_error (myconn));
        return (1);
    }

    /* set reconnect on */
    mysql_options(myconn, MYSQL_OPT_RECONNECT, &reconnect);
    return (0);
}

static void 
logto_db(MYSQL * myconn, char * tblname, char * lbuf) {
     char query[LOGFILE_BUF_LEN + 512];
     char *fld[15];
     int fc=0;

     fld[0]=strtok(lbuf, " ");
     while (fld[fc] != NULL) {
        fc++;
        fld[fc]=strtok(NULL, " ");
     }
     fld[fc-1]=strtok(fld[fc-1], "\r\n");
     if ( fld[fc-1] == NULL ) 
        fc--;  
     if ( fc == COLUMN_COUNT ) {
        memset (query, 0, strlen (query) + 1);

        /* logformat mysql_columns %ts.%03tu %tr %>a %Ss %Hs %<st %rm %ru %Sh %un %<A %mt */
        sprintf (query, "INSERT INTO %s VALUES ('%f', '%d', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s', '%s')", tblname, \
            atof(fld[0]), atoi(fld[1]), fld[2], fld[3], fld[4], atoi(fld[5]), \
            fld[6], fld[7], fld[8], fld[9], fld[10], fld[11]);

#ifdef LDM_DEBUG
         fprintf(stdout, "QUERY: %s\n",query);
#endif
         /* when connection drops just log it */
         if (mysql_query (myconn, query)) { 
            syslog (LOG_WARNING, "Error %d: %s", mysql_errno (myconn), mysql_error (myconn));
            /* reconnect to mysql */
            mysql_ping(myconn);
         }
     } 
#ifdef LDM_DEBUG
     else {
         fprintf(stdout, "Error: Received incorrect column count from squid: %d\n", fc);
         syslog(LOG_WARNING, "Error: Received incorrect column count from squid: %d\n", fc);
     }
#endif
}

/*
 * The commands:
 *
 * L<data>\n - logfile data
 * R\n - rotate file
 * T\n - truncate file
 * O\n - repoen file
 * F\n - flush file
 * r<n>\n - set rotate count to <n>
 * b<n>\n - 1 = buffer output, 0 = don't buffer output
 */

int
main(int argc, char *argv[]) {
    int t;
    char buf[LOGFILE_BUF_LEN];
    MYSQL connect;
    struct dbconf dbcf;

    if (argc < 2) {
	fprintf(stdout,"Error: usage: %s <db.configfile>\n", argv[0]);
	exit(1);
    }
    setbuf(stdout, NULL);
    close(2);
    t = open(_PATH_DEVNULL, O_RDWR);
    assert(t > -1);
    dup2(t, 2);
#ifndef LDM_DEBUG
    /* supress the o/p incase */
    close(1);
    dup2(t, 1);
#endif
    if (parse (argv[1], &dbcf) != 0) {
        fprintf (stdout, "Error: parsing db.configfile\n");
        exit (1);
    }

    if (db_connect(&connect, dbcf) != 0) 
       exit(1);

    while (fgets(buf, LOGFILE_BUF_LEN, stdin)) {
	/* First byte indicates what we're logging! */
	switch (buf[0]) {
	case 'L':
	    if (buf[1] != '\0') {
               logto_db(&connect, dbcf.db_tablename, buf+1);
	    }
	    break;
	case 'R':
            syslog (LOG_INFO, "Squid log-rotating");
            // mysql_close (&connect);
            /* placeholder */
            // rotate_tbl/db ();
            // if (db_connect(&connect, dbcf) != 0) exit(1);
	    break;
	case 'T':
	    break;
	case 'O':
	    break;
	case 'r':
	    break;
	case 'b':
	    break;
	case 'F':
#ifdef LDM_DEBUG
            syslog (LOG_INFO, "Squid log commiting to db");
#endif
            if (mysql_commit(&connect) != 0) {
               syslog(LOG_ERR, "commit failed");
            }
	    break;
	default:
	    break;
	}
    }
    mysql_close (&connect);
    exit(0);
}
