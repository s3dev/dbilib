/*
    Purpose:    Procedure for adding a new guitar.

    Author:     J. Berendt
    Date:       2023-05-18
    Revision:   1

    Updates:
    1:  Written.
*/

DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_insert_guitars_add_new`$$
CREATE PROCEDURE `sp_insert_guitars_add_new` (IN _make VARCHAR(25),
                                              IN _model VARCHAR(25),
                                              IN _colour VARCHAR(25))
BEGIN

    INSERT INTO `guitars` (
        `make`, 
        `model`, 
        `colour`
    ) VALUES (
        _make,
        _model,
        _colour
    );

END$$
DELIMITER ;

