/* pre-defined variables variable and default value */

/* hostname */
#define VAR_HOST_NAME "hostname"
#define DEF_HOST_NAME "localhost"

/* username */
#define VAR_USER_NAME "user"
#define DEF_USER_NAME "squid"

/* user's (above) password */
#define VAR_USER_PASSWORD "password"
#define DEF_USER_PASSWORD "squid"

/* database name */
#define VAR_DATABASE_NAME "database"
#define DEF_DATABASE_NAME "mysql_auth"

/* socket name */
/* Currently NOT used in the code*/
#define VAR_MYSQLD_SOCKET "mysqld_socket"
#define DEF_MYSQLD_SOCKET "/var/lib/mysql/mysqld.sock"

/* table name */
#define VAR_TABLE_NAME "table"
#define DEF_TABLE_NAME "data"

/* max length of username or passwords */
#define MAX_STRLEN 64

/* max length of line in config file */
#define MAXLENGTH 512

/* structure for variable options */

struct dbconf {
	char *db_hostname;
	char *db_username;
	char *db_password;
	char *db_dbname;
	char *db_mysqld_socket;
	char *db_tablename;
};

