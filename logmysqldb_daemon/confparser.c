/* confparser.c
 *  * (C) 2002 Ervin Hegedus
 *  * Released under GPL, see COPYING-2.0 for details.
 * Modified By : ViSolve
*/

#include <stdio.h>
#include <syslog.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "define.h"

int
parse (char *config_file, struct dbconf *cf) {
  FILE *fp;
  char line[MAXLENGTH];
  char *var, *value;
  int i = 0;

  if ((fp = fopen (config_file, "r"), fp == NULL)) {
      printf ("%s No such file or directory\n", config_file);
      syslog (LOG_WARNING, "Unable to open db configfile: %s\n", config_file);
      return 1;
    }

  /*
   * setting up default values to cf
   */
  cf->db_hostname = malloc (strlen (DEF_HOST_NAME) + 1);
  strcpy (cf->db_hostname, DEF_HOST_NAME);

  cf->db_username = malloc (strlen (DEF_USER_NAME) + 1);
  strcpy (cf->db_username, DEF_USER_NAME);

  cf->db_password = malloc (strlen (DEF_USER_PASSWORD) + 1);
  strcpy (cf->db_password, DEF_USER_PASSWORD);

  cf->db_dbname = malloc (strlen (DEF_DATABASE_NAME) + 1);
  strcpy (cf->db_dbname, DEF_DATABASE_NAME);

  cf->db_mysqld_socket = malloc (strlen (DEF_MYSQLD_SOCKET) + 1);
  strcpy (cf->db_mysqld_socket, DEF_MYSQLD_SOCKET);

  cf->db_tablename = malloc (strlen (DEF_TABLE_NAME) + 1);
  strcpy (cf->db_tablename, DEF_TABLE_NAME);

  /*
   * reading and parsing lines
   */
  while (fgets (line, MAXLENGTH, fp) != NULL) {
      i++;
      if (line[0] != '#' && line[0] != '\n') {
          var = strtok (line, " \t");
          if (var == NULL) {
             syslog (LOG_WARNING, "Parse error at configfile line: %d.", i);
          } else {
             value = strtok (NULL, " \t\n");
             if (value == NULL) {
                syslog (LOG_WARNING, "Parse error at db configfile line: %d.", i);
             } else {

                  if (strcmp (var, VAR_HOST_NAME) == 0) {
                      free (cf->db_hostname);
                      cf->db_hostname = malloc (strlen (value) + 1);
                      strcpy (cf->db_hostname, value);
                  }

                  if (strcmp (var, VAR_USER_NAME) == 0) {
                      free (cf->db_username);
                      cf->db_username = malloc (strlen (value) + 1);
                      strcpy (cf->db_username, value);
                  }

                  if (strcmp (var, VAR_USER_PASSWORD) == 0) {
                      free (cf->db_password);
                      cf->db_password = malloc (strlen (value) + 1);
                      strcpy (cf->db_password, value);
                  }

                  if (strcmp (var, VAR_DATABASE_NAME) == 0) {
                      free (cf->db_dbname);
                      cf->db_dbname = malloc (strlen (value) + 1);
                      strcpy (cf->db_dbname, value);
                  }

                  if (strcmp (var, VAR_MYSQLD_SOCKET) == 0) {
                      free (cf->db_mysqld_socket);
                      cf->db_mysqld_socket = malloc (strlen (value) + 1);
                      strcpy (cf->db_mysqld_socket, value);
                  }

                  if (strcmp (var, VAR_TABLE_NAME) == 0) {
                      free (cf->db_tablename);
                      cf->db_tablename = malloc (strlen (value) + 1);
                      strcpy (cf->db_tablename, value);
                  }

             }
          }
      }
  }

  fclose (fp);
  return 0;
}
