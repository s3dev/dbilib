/*
    Purpose:    Create a view listing all Fender guitars from the guitars
                table.
    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/

CREATE VIEW [dbo].[v_guitars_fender]
AS

    SELECT 
        *
    FROM
        [dbilib_test].[dbo].[guitars]
    WHERE
        [make] = 'fender';

