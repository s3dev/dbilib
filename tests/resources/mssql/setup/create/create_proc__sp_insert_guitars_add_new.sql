/*
    Purpose:    Procedure for adding a new guitar.

    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/

CREATE OR ALTER PROCEDURE [usp_insert_guitars_add_new] (@_make VARCHAR(25),
														@_model VARCHAR(25),
							                            @_colour VARCHAR(25))
AS BEGIN

    SET NOCOUNT ON;

    INSERT INTO [dbilib_test].[dbo].[guitars] (
        [make], 
        [model], 
        [colour]
    ) VALUES (
        @_make,
        @_model,
        @_colour
    );

	COMMIT;

	/* 
    Return the ID for the inserted/updated field.
    This is used rather than SCOPE_IDENTITY() as the correct ID is 
    only returned on *insert* and returns the wrong ID 
    (i.e. previous insert ID) if the record is updated.
	*/
    SELECT TOP 1
		[id] 
	FROM 
		[dbilib_test].[dbo].[guitars] 
	WHERE 
		[make] = @_make 
		AND [model] = @_model 
		AND [colour] = @_colour;

END
