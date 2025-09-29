prompt = """
Given a entity and a list of attribute names, your task is to extract the attribute value for each attribute name from the provided text. If the value of some attribute is not mentioned in the text, please output "None" for this attribute.
Here is an example:

Input:
Text: The song 'Shape of You' by Ed Sheeran was released on January 6, 2017. 'Thinking Out Loud', another hit by him, was released on September 24, 2014.

Entity: Shape of You

Attribute Names: 
Releasing date
Singer
Genre


Output:
January 6, 2017
Ed Sheeran
None

Using the format provided above, extract attribute values for the given entity and attribute names from the text. Please strictly follow the output format like the given example and do not output any extra words.
"""