/*
    Purpose:    Create a view listing all Fender guitars from the guitars
                table.
    Author:     J. Berendt
    Date:       2023-05-17
    Revision:   1

    Updates:
    1:  Written.
*/

CREATE OR REPLACE VIEW `v_guitars_fender`
AS

    SELECT 
        *
    FROM
        `guitars`
    WHERE
        `make` = 'fender';

