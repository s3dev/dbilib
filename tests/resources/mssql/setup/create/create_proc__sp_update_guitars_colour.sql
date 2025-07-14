/*
    Purpose:    Update the 'colour' field for a given guitar.
    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/

CREATE OR ALTER PROCEDURE [usp_update_guitars_colour] (@_id INTEGER,
													   @_colour VARCHAR(25))
AS BEGIN

    UPDATE 
        [dbilib_test].[dbo].[guitars]
    SET 
        [colour] = @_colour
    WHERE
        [id] = @_id;

	COMMIT;

END
