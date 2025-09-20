/*
    Purpose:    Procedure for adding a new player to the test table.

    Author:     J. Berendt
    Date:       2025-07-14
    Revision:   1

    Updates:
    1:  Written.
*/

CREATE OR ALTER PROCEDURE [usp_insert_players_add_new] (@_guitars_id INTEGER,
					                                    @_name VARCHAR(50))
AS BEGIN

	SET NOCOUNT ON;

    INSERT INTO [dbilib_test].[dbo].[players] (
        [guitars_id], 
        [name] 
    ) VALUES (
        @_guitars_id,
        @_name
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
		[dbilib_test].[dbo].[players] 
	WHERE 
		[guitars_id] = @_guitars_id
		AND [name] = @_name;
		
END
