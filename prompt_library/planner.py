


prompt_di = """
I am working on developing an automatic system for dataset population. Specifically, given a database schema, a user instruction, and the background text, the system aims to populate database with the desired information extracted from the text according to the user instruction. 

Currently, you need to act as a code generation model, that considering the user instruction and the database schema (especially the interdependency between the tables), determines the sequence of the modules and output the executive python code which calls for these modules sequentially to solve the dataset population task. 

The modules are defined as follows:

- Named_Entity_Recognition(text: str, type: str) -> list  
- For the given background text and the entity type, this module is to extract all the entities of the specified type from the text. 

- Relation_Extraction(text: str, head_e:list, relation: str) -> list
- Given a text, a list of entities and a relation type, this module is to extract all the tail entities for each head entity considering this relation type from the provided text.

- Attribute_Extraction(text: str, entity: str, attribute_list: list) -> dict
- Given the background text, an entity, and a list of attribute names, this module is to extract the attribute values for each attribute name from the provided text.

- Text_Classification(text: str, label_list: list) -> str
- Given a text and a list of labels, this module is to classify the text into one label.

- Data_Normalization(data_entries: list, database: dict, table_name: str, data_format: dict=None) -> list
- Given a list of data entries whose keys are the column name of the values, and an existing database, transform these data entries to match the schema of one table in the database. The function output is the normalized data entries.   

- Entity_Linking(data_entries: list, database: dict, table_name: str) -> list
- Given an existing database, a table name, and a list of data entries, this module is to link these entities with some existing rows in the database. Finally, this function outputs a list of data index. 

- Infill_Data(data_entries: list, database: dict, table_name: str) -> dict 
- Given some data entries, an existing database, and a table name in this database, this module is to infill missing values in one table of database with the data entries. The output is the updated database. 


Below are three examples of different task types using the same database:


Input:
Database Schema:
Type: table Name: singer
SQL: CREATE TABLE singer
(
    SingerID           INTEGER
        constraint single_pk
            primary key,
    Name              TEXT,
    "Date of Birth"   DATE,
    "Birth City"      TEXT,
    "Birth Country"   TEXT,
    "Height (Inches)" INTEGER,
    Biography         TEXT,
    Gender            TEXT,
    Ethnicity         TEXT,
    NetWorth          TEXT
)

Type: table Name: album
SQL: CREATE TABLE album
(
    AlbumID        INTEGER
        constraint album_pk
            primary key,
    SingerID       INTEGER,
    Title          TEXT,
    "Release Date" TEXT,
    Genre          TEXT,
    Rating         REAL,
    primary key (AlbumID, SingerID),
    foreign key (AlbumID) references album(AlbumID),
    foreign key (SingerID) references singer(SingerID)
)




Example 1:

User Instruction: 
Given a document about three singles, update their date of birth and birth city into the database.

Output:
# a. Determine the task type based on the user instruction
task_type = 'data infilling'
# List the targeted attributes explicitly mentioned by the user instruction. Otherwise, infer based on database schema.
target_attributes = ["Date of Birth", "Birth City"]

# b. Extract singer information
# (1) Extract singer's name, which is the table name or the primary key, using Named_Entity_Recognition
singer_names = Named_Entity_Recognition(text, "singer")

all_singer_data = []
for _id, singer_name in enumerate(singer_names): 
    # (2) Extract the attributes using Attribute_Extraction
    singer_attributes = Attribute_Extraction(text, singer_name, target_attributes)
    singer_attributes['Name'] = singer_name
    all_singer_data.append(singer_attributes)

# (3) Normalize the extracted attributes to fit the singer table schema using Data_Normalization
normalized_singer_data = Data_Normalization(all_singer_data, database, table_name='singer')
print(normalized_singer_data)

# (4) Popluate the new rows into the database 
Infill_Data(normalized_singer_data, database, table_name='singer')



Example 2:

User Instruction: 
Recover the values of the empty columns for the row of singer 'Alice Wang' based on the reference text.

Output:
# a. Determine the task type based on the user instruction
task_type = 'data infilling'
# List the targeted attributes explicitly mentioned by the user instruction. Otherwise, infer based on database schema.
target_attributes = ["Date of Birth", "Birth City", "Birth Country", "Height (Inches)", "Biography", "Gender", "Ethnicity", "NetWorth"]
    
# b. Extract singer information
# (1) List the named entities if explicitly mentioned by the user instruction. Otherwise, extract singer's name, which is the table name or the primary key, using Named_Entity_Recognition
singer_names = ['Alice Wang']

all_singer_data = []
for _id, singer_name in enumerate(singer_names): 
    # (2) Extract the attributes using Attribute_Extraction
    singer_attributes = Attribute_Extraction(text, singer_name, target_attributes)
    singer_attributes['Name'] = singer_name
    all_singer_data.append(singer_attributes)

# (3) Normalize the extracted attributes to fit the singer table schema using Data_Normalization
normalized_singer_data = Data_Normalization(all_singer_data, database, table_name='singer')
print(normalized_singer_data)

# (4) Popluate the new rows into the database 
Infill_Data(normalized_singer_data, database, table_name='singer')




Using the format provided above, generate the plan for database population given the inputs. The code can directly use four parameters, including instruction, text,  database_schema, and database. But don't assume the value for any other parameter. 
Importantly, don't output any other information but the code.


"""






prompt_rp = """
I am working on developing an automatic system for dataset population. Specifically, given a database schema, a user instruction, and the background text, the system aims to populate database with the desired information extracted from the text according to the user instruction. 

Currently, you need to act as a code generation model, that considering the user instruction and the database schema (especially the interdependency between the tables), determines the sequence of the modules and output the executive python code which calls for these modules sequentially to solve the dataset population task. 

The modules are defined as follows:

- Named_Entity_Recognition(text: str, type: str) -> list  
- For the given background text and the entity type, this module is to extract all the entities of the specified type from the text. 

- Relation_Extraction(text: str, head_e:list, relation: str) -> list
- Given a text, a list of entities and a relation type, this module is to extract all the tail entities for each head entity considering this relation type from the provided text.

- Attribute_Extraction(text: str, entity: str, attribute_list: list) -> dict
- Given the background text, an entity, and a list of attribute names, this module is to extract the attribute values for each attribute name from the provided text.

- Text_Classification(text: str, label_list: list) -> str
- Given a text and a list of labels, this module is to classify the text into one label.

- Data_Normalization(data_entries: list, database: dict, table_name: str, data_format: dict=None) -> list
- Given a list of data entries whose keys are the column name of the values, and an existing database, transform these data entries to match the schema of one table in the database. The function output is the normalized data entries.   

- Entity_Linking(data_entries: list, database: dict, table_name: str) -> list
- Given an existing database, a table name, and a list of data entries, this module is to link these entities with some existing rows in the database. Finally, this function outputs a list of data index. 

- Populate_Row(data_entries: list, database: dict, table_name: str) -> dict 
- Given some data entries, an existing database, and a table name in this database, this module is to populate the table with the data entries by add new rows. The output is the updated database. 


Below are three examples of different task types using the same database:


Input:
Database Schema:
Type: table Name: singer
SQL: CREATE TABLE singer
(
    SingerID           INTEGER
        constraint single_pk
            primary key,
    Name              TEXT,
    "Date of Birth"   DATE,
    "Birth City"      TEXT,
    "Birth Country"   TEXT,
    "Height (Inches)" INTEGER,
    Biography         TEXT,
    Gender            TEXT,
    Ethnicity         TEXT,
    NetWorth          TEXT
)

Type: table Name: album
SQL: CREATE TABLE album
(
    AlbumID        INTEGER
        constraint album_pk
            primary key,
    SingerID       INTEGER,
    Title          TEXT,
    "Release Date" TEXT,
    Genre          TEXT,
    Rating         REAL,
    primary key (AlbumID, SingerID),
    foreign key (AlbumID) references album(AlbumID),
    foreign key (SingerID) references singer(SingerID)
)




Example 1:

User Instruction: 
Given a document about three singles, update their date of birth and birth city into the database.

Output:
# a. Determine the task type based on the user instruction
task_type = 'row population'

# b. Extract singer information
# (1) Extract singer's name, which is the table name or the primary key, using Named_Entity_Recognition
singer_names = Named_Entity_Recognition(text, "singer")
# Find out the primary key, singer_ids
singer_ids = {}

all_singer_data = []
for _id, singer_name in enumerate(singer_names): 
    # (2) Extract attributes for the singer using Attribute_Extraction
    singer_attributes = Attribute_Extraction(text, singer_name, ["Date of Birth", "Birth City", "Birth Country", "Height (Inches)", "Biography", "Gender", "Ethnicity", "NetWorth"])
    singer_attributes['Name'] = singer_name

    # (3) Calculate the row index based on the existing data entries if the database schema includes such the index
    singer_attributes['SingerID'] = int(database['singer'][-1]['SingerID']) + _id + 1
    singer_ids[singer_name] = singer_attributes['SingerID']
    all_singer_data.append(singer_attributes)

# (4) Normalize the extracted attributes to fit the singer table schema using Data_Normalization
normalized_singer_data = Data_Normalization(all_singer_data, database, table_name='singer')
print(normalized_singer_data)

# (5) Popluate the new rows into the database 
Populate_Row(normalized_singer_data, database, table_name='singer')

# c. Extract album information
# (1) Extract album title using Named_Entity_Recognition
album_titles = Named_Entity_Recognition(text, "album")

all_album_data = []
for _id, album_title in enumerate(album_titles):
    # (2) Extract attributes for the album using Attribute_Extraction
    # Since the background text doesn't provide all the necessary information, some fields will be left blank
    album_attributes = Attribute_Extraction(text, album_title, ["Release Date", "Genre", "Rating"])
    album_attributes['Title'] = album_title

    # (3) Link the SingerID to the album data
    singer_name = Attribute_Extraction(text, album_title, ["Singer"])
    album_attributes['SingerID'] = singer_ids[singer_name] if singer_name in singer_ids else None

    # (4) Calculate the row index based on the existing data entries if the database schema includes such the index
    album_attributes['AlbumID'] = int(database['album'][-1]['AlbumID']) + _id + 1
    all_album_data.append(album_attributes)

# (5) Normalize the extracted attributes to fit the album table schema using Data_Normalization
normalized_album_data = Data_Normalization(all_album_data, database, table_name='album')
print(normalized_album_data)

# (6) Popluate the new rows into the database 
Populate_Row(normalized_album_data, database, table_name='album')



Using the format provided above, generate the plan for database population given the inputs. The code can directly use four parameters, including instruction, text,  database_schema, and database. But don't assume the value for any other parameter. 
Importantly, don't output any other information but the code.


"""





prompt_ca = """
I am working on developing an automatic system for dataset population. Specifically, given a database schema, a user instruction, and the background text, the system aims to populate database with the desired information extracted from the text according to the user instruction. 

Currently, you need to act as a code generation model, that considering the user instruction and the database schema (especially the interdependency between the tables), determines the sequence of the modules and output the executive python code which calls for these modules sequentially to solve the dataset population task. 

The modules are defined as follows:

- Named_Entity_Recognition(text: str, type: str) -> list  
- For the given background text and the entity type, this module is to extract all the entities of the specified type from the text. 

- Relation_Extraction(text: str, head_e:list, relation: str) -> list
- Given a text, a list of entities and a relation type, this module is to extract all the tail entities for each head entity considering this relation type from the provided text.

- Attribute_Extraction(text: str, entity: str, attribute_list: list) -> dict
- Given the background text, an entity, and a list of attribute names, this module is to extract the attribute values for each attribute name from the provided text.

- Text_Classification(text: str, label_list: list) -> str
- Given a text and a list of labels, this module is to classify the text into one label.

- Data_Normalization(data_entries: list, database: dict, table_name: str, data_format: dict=None) -> list
- Given a list of data entries whose keys are the column name of the values, and an existing database, transform these data entries to match the schema of one table in the database. The function output is the normalized data entries.   

- Entity_Linking(data_entries: list, database: dict, table_name: str) -> list
- Given an existing database, a table name, and a list of data entries, this module is to link these entities with some existing rows in the database. Finally, this function outputs a list of data index. 

- Add_Column(data_entries: list, database: dict, table_name: str, new_columns: list) -> dict 
- Given some data entries, an existing database, a table name, and a list of new column names in this database, this module is to add new columns into a table of the database with the data entries. The output is the updated database. 


Below are three examples of different task types using the same database:


Input:
Database Schema:
Type: table Name: singer
SQL: CREATE TABLE singer
(
    SingerID           INTEGER
        constraint single_pk
            primary key,
    Name              TEXT,
    "Date of Birth"   DATE,
    "Birth City"      TEXT,
    "Birth Country"   TEXT,
    "Height (Inches)" INTEGER,
    Biography         TEXT,
    Gender            TEXT,
    Ethnicity         TEXT,
    NetWorth          TEXT
)

Type: table Name: album
SQL: CREATE TABLE album
(
    AlbumID        INTEGER
        constraint album_pk
            primary key,
    SingerID       INTEGER,
    Title          TEXT,
    "Release Date" TEXT,
    Genre          TEXT,
    Rating         REAL,
    primary key (AlbumID, SingerID),
    foreign key (AlbumID) references album(AlbumID),
    foreign key (SingerID) references singer(SingerID)
)




Example 1:

User Instruction: 
Given a document about some singles, add two new columns into the database: The first is Date of Birth, which means the date of birth of a single. The values should in the format of MM-DD-YYYY. The other column is Height, which means the height of the singer. The value unit is cm. The default value is None. 

Output:
# a. Determine the task type based on the user instruction
task_type = 'column addition'

# b. Extract singer information
# (1) Extract singer's name, which is the table name or the primary key, using Named_Entity_Recognition
singer_names = Named_Entity_Recognition(text, "singer")


# (2) Extract attributes for the singer using Attribute_Extraction. Here the attributes are the new columns according to the user instruction.
all_singer_data = []
new_columns = ['Date of Birth', 'Height']
for _id, singer_name in enumerate(singer_names): 
    singer_attributes = Attribute_Extraction(text, singer_name, new_columns)
    singer_attributes['Name'] = singer_name
    all_singer_data.append(singer_attributes)

# (4) Normalize the extracted attributes to fit the singer table schema using Data_Normalization
# for column addition, the data format for the new column should be defined, including the data description, the data type and any special requirement if needed. 
data_format = {"Date of Birth": "date of birth of a single, Text, MM-DD-YYYY", "Height": "height of a single, Text, Value unit is cm"}
normalized_singer_data = Data_Normalization(all_singer_data, database, table_name='singer', data_format=data_format)
print(normalized_singer_data)

# (5) Popluate the new columns into the database 
Add_Column(normalized_singer_data, database, table_name='singer', new_columns=new_columns)


Using the format provided above, generate the plan for database population given the inputs. The code can directly use four parameters, including instruction, text,  database_schema, and database. But don't assume the value for any other parameter. 
Importantly, don't output any other information but the code.


"""



prompt = {'di': prompt_di, 'rp': prompt_rp, 'ca': prompt_ca}