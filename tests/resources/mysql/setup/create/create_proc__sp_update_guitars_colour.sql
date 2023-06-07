/*
    Purpose:    Update the 'colour' field for a given guitar.
    Author:     J. Berendt
    Date:       2023-05-17
    Revision:   1

    Updates:
    1:  Written.
*/

DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_update_guitars_colour`$$
CREATE PROCEDURE `sp_update_guitars_colour` (IN _id INTEGER,
                                             IN _colour VARCHAR(25))
BEGIN

    UPDATE 
        `guitars`
    SET 
        `colour` = _colour
    WHERE
        `id` = _id;

END$$
DELIMITER ;

