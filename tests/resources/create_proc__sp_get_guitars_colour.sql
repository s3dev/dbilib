/*
    Purpose:    Collect all guitars of a given colour.
    Author:     J. Berendt
    Date:       2023-05-17
    Revision:   1

    Updates:
    1:  Written.
*/

DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_get_guitars_colour`$$
CREATE PROCEDURE `sp_get_guitars_colour` (IN _colour VARCHAR(25))

BEGIN

    SELECT
        *
    FROM
        `guitars`
    WHERE
        `colour` = _colour
    ORDER BY
        `model`;

END$$
DELIMITER ;

