prompt = """
Given a list of entities and a relation type, your task is to extract all the tail entities for each head entity considering this relation type from the provided text. 
Here is an example:

Input:
Text: The song 'Shape of You' by Ed Sheeran was released on January 6, 2017. 'Thinking Out Loud', another hit by him, was released on September 24, 2014.
Entity: Shape of You, Thinking Out Loud
Relation Type: Releasing date

Output:
January 6, 2017
September 24, 2014

Using the format provided above, extract the tail entities for each head entity according to the relation type from the text. Please strictly follow the output format like the given example and do not output any extra words.
"""