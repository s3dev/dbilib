/*
    Purpose:    Deconstruct the testing database.
    Author:     J. Berendt
    Date:       2023-05-18
    Revision:   1

    Updates:
    1:  Written.
*/

DROP VIEW `dbilib_test`.`v_guitars_fender`;
DROP PROCEDURE `dbilib_test`.`sp_get_guitars_colour`;
DROP PROCEDURE `dbilib_test`.`sp_insert_guitars_add_new`;
DROP PROCEDURE `dbilib_test`.`sp_insert_players_add_new`;
DROP PROCEDURE `dbilib_test`.`sp_update_guitars_colour`;
DROP TABLE `dbilib_test`.`guitars`;
DROP TABLE `dbilib_test`.`players`;

