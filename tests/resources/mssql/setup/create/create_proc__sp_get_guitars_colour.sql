/*
    Purpose:    Collect all guitars of a given colour.
    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/

CREATE OR ALTER PROCEDURE [usp_get_guitars_colour] (@_colour VARCHAR(25))

AS BEGIN

    SELECT
        *
    FROM
        [dbilib_test].[dbo].[guitars]
    WHERE
        [colour] = @_colour
    ORDER BY
        [model];

END
