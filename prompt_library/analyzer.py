prompt = """
Given a database including its schema and some existing data entries, summarize the database into a brief description for each column in every table. This description should include: 
column_name
column_description
data_format
value_description (data unit, special data format, label space for the values)


For example: 

Input:

Database schema:
CREATE TABLE "movie" (
	"MovieID"	INTEGER,
	"Title"	TEXT,
	"MPAA Rating"	TEXT,
	"Budget"	INTEGER,
	"Gross"	INTEGER,
	"Release Date"	TEXT,
	"Genre"	TEXT,
	"Runtime"	INTEGER,
	"Rating"	REAL,
	"Rating Count"	INTEGER,
	"Summary"	TEXT,
    "DirectorID"	INTEGER,
	CONSTRAINT "movie_pk" PRIMARY KEY("MovieID")
    FOREIGN KEY("DirectorID") REFERENCES "director"("DirectorID"),
);

Existing data entries:
1	Look Who's Talking	PG-13	7500000	296000000	1989-10-12	Romance	93	5.9	73638 1
2	Driving Miss Daisy	PG	7500000	145793296	1989-12-13	Comedy	99	7.4	91075 2 
3	Turner & Hooch	PG	13000000	71079915	1989-07-28	Crime	100	7.2	91415 100
4	Born on the Fourth of July	R	14000000	161001698	1989-12-20	War	145	7.2	91415 1000
5	Field of Dreams	PG	15000000	84431625	1989-04-21	Drama	107	7.5	101702 1234
6	Uncle Buck	PG	15000000	79258538	1989-08-16	Family	100	7.0	77659 1231
7	When Harry Met Sally...	R	16000000	92800000	1989-07-21	Romance	96	7.6	 180871 129


Output:
MovieID: Unique identifier for each movie. Format: Integer.
Title: Name of the movie. Format: Text.
MPAA Rating: Motion picture association of america rating. Content suitability rating. Format: Text. Label space includes G, PG, PG-13, R, NC-17.
Budget: Production budget in dollars. Format: Integer.
Gross: Box office revenue in dollars. Format: Integer.
Release Date: Date of release. Format: Text (yyyy-mm-dd).
Runtime: Duration in minutes. Format: Integer.
Rating: Audience rating, 0.0 to 10.0 where higher is better. Format: Real.
Rating Count: Total number of ratings received. Format: Integer.
Summary: Brief synopsis of the movie. Format: Text.
DirectorID: Identifier for the director, linking to the "director" table. Format: Integer.


Following the example above, generate a brief description for the following database:


"""



