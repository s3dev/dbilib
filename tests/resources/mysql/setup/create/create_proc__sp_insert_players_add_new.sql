/*
    Purpose:    Procedure for adding a new player to the test table.

    Author:     J. Berendt
    Date:       2023-05-18
    Revision:   1

    Updates:
    1:  Written.
*/

DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_insert_players_add_new`$$
CREATE PROCEDURE `sp_insert_players_add_new` (IN _guitars_id INTEGER,
                                              IN _name VARCHAR(50))
BEGIN

    INSERT INTO `players` (
        `guitars_id`, 
        `name` 
    ) VALUES (
        _guitars_id,
        _name
    );

END$$
DELIMITER ;

