import sqlite3
from openai import OpenAI

def get_openai_key():
    with open('key.txt', 'r') as f:
        return f.read().strip()
    
client = OpenAI(api_key=get_openai_key())

def get_ai_response(prompt):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    responseList = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            responseList.append(chunk.choices[0].delta.content)

    result = "".join(responseList)
    return result

connection = sqlite3.connect('recipes.db')

cursor = connection.cursor()

drop_tables_sql = '''
    drop table if exists recipe_ingredient;
    drop table if exists ingredient;
    drop table if exists recipe;
'''

create_tables_sql = '''
    create table ingredient (
        id integer primary key,
        name text,
        serving_size integer,
        carbohydrate integer,
        fat integer,
        protein integer
    );
    
    create table recipe (
        id integer primary key,
        name text
    );
               
    create table recipe_ingredient (
        recipe_id integer,
        ingredient_id integer,
        weight real,
        primary key (recipe_id, ingredient_id),
        foreign key (recipe_id) references recipe(id),
        foreign key (ingredient_id) references ingredient(id)
    )
'''

for sql in drop_tables_sql.split(';'):
    cursor.execute(sql)
for sql in create_tables_sql.split(';'):
    cursor.execute(sql)

insert_sql = '''
    insert into ingredient (name, serving_size, carbohydrate, fat, protein) values
    ('rice', 100, 28, 0, 3),
    ('chicken breast', 100, 0, 1, 30),
    ('broccoli', 100, 7, 0, 3),
    ('olive oil', 100, 0, 100, 0),
    ('salt', 100, 0, 0, 0),
    ('pepper', 100, 0, 0, 0),
    ('garlic', 100, 16, 0, 1),
    ('onion', 100, 9, 0, 1),
    ('carrot', 100, 9, 0, 1),
    ('celery', 100, 3, 0, 0),
    ('beef', 100, 0, 5, 20),
    ('tomato', 100, 4, 0, 1),
    ('pasta', 100, 25, 1, 5),
    ('milk', 100, 5, 3, 3),
    ('flour', 100, 73, 1, 10),
    ('butter', 100, 0, 81, 1),
    ('cheese', 100, 2, 34, 24),
    ('egg', 100, 1, 10, 13),
    ('bacon', 100, 0, 42, 37),
    ('lettuce', 100, 2, 0, 1),
    ('mayonnaise', 100, 0, 83, 0),
    ('tomato sauce', 100, 7, 0, 1),
    ('sugar', 100, 100, 0, 0),
    ('soy sauce', 100, 15, 0, 6),
    ('sesame oil', 100, 0, 100, 0),
    ('ginger', 100, 18, 0, 2),
    ('chicken thigh', 100, 0, 9, 20),
    ('pork', 100, 0, 6, 20),
    ('beef', 100, 0, 5, 20),
    ('shrimp', 100, 0, 1, 24),
    ('fish', 100, 0, 5, 20),
    ('tofu', 100, 2, 4, 8),
    ('cabbage', 100, 6, 0, 1),
    ('mushroom', 100, 3, 0, 3);
               
    insert into recipe (name) values
    ('chicken and rice'),
    ('beef and broccoli'),
    ('spaghetti carbonara'),
    ('caesar salad'),
    ('beef stew'),
    ('chicken stir fry');
    
    insert into recipe_ingredient (recipe_id, ingredient_id, weight) values
    (1, 1, 8),
    (1, 2, 16),
    (1, 4, 2),
    (1, 5, 1),
    (1, 6, 1),
    (1, 7, 1),
    (1, 8, 1),
    (1, 9, 1),
    (2, 11, 8),
    (2, 3, 8),
    (2, 4, 2),
    (2, 5, 1),
    (2, 6, 1),
    (2, 7, 1),
    (2, 8, 1),
    (2, 9, 1),
    (3, 13, 8),
    (3, 16, 2),
    (3, 17, 1),
    (3, 18, 1),
    (3, 19, 1),
    (3, 20, 1),
    (3, 21, 1),
    (3, 22, 1),
    (4, 18, 2),
    (4, 19, 1),
    (4, 20, 1),
    (4, 23, 1),
    (4, 24, 1),
    (4, 25, 1),
    (4, 26, 1),
    (4, 27, 1),
    (5, 11, 8),
    (5, 3, 8),
    (5, 4, 2),
    (5, 5, 1),
    (5, 6, 1),
    (5, 7, 1),
    (5, 8, 1),
    (5, 9, 1),
    (6, 1, 8),
    (6, 2, 16),
    (6, 4, 2),
    (6, 5, 1),
    (6, 6, 1),
    (6, 7, 1),
    (6, 8, 1),
    (6, 9, 1)
'''

for sql in insert_sql.split(';'):
    cursor.execute(sql)

questions = [
    "What is the total fat in the recipe 'beef and broccoli'?",
    "What is the total protein in the recipe 'spaghetti carbonara'?",
    "How many calories are in the recipe 'caesar salad'?",
    "How many ounces of beef are in the recipe 'beef stew'?",
    "How many ingredients are in the recipe 'chicken stir fry'?",
    "What are some recipes that contain chicken breast?",
    "What percent of the recipe 'chicken and rice' by weight is protein?",
    "What recipe has the least fat?",
    "Are there any recipes without meat, and if so, what are they?",
    "Which recipes have more fat than carbohydrates?"
]

preamble = ("There is a SQLite database that contains information about recipes and their ingredients. "
            "Weight values recipe_ingredient table are in ounces. User queries asking for total weight should be answered in grams unless othewise specified. "
            "The database has three tables with the following create statements: \n")
preamble += create_tables_sql
one_shot_prompt = """Here is an example question and a corresponding SQL query that answers it:

Question: What is the total carbohydrate in the recipe 'chicken and rice'?
SQL Query: 
    select sum(i.carbohydrate * ri.weight / i.serving_size) * 28.3495 as total_carbohydrate
    from recipe r
    join recipe_ingredient ri on r.id = ri.recipe_id
    join ingredient i on ri.ingredient_id = i.id
    where r.name = 'chicken and rice';
"""

def ask_questions(one_shot):
    for i, question in enumerate(questions):
        print(f"Question {i+1}: {question}\n")
        prompt = preamble
        if one_shot:
            prompt += one_shot_prompt + "\n"
        prompt += ("\n\nPlease create an SQL query that answers the following question. "
                "Only include the SQL query text in your response. "
                "Do not include any other text in your response, including any sql text formatting characters.\n\n")
        prompt += question
        sql = get_ai_response(prompt)
        print("SQL Query: \n" + sql + "\n")
        sql_result = None
        try:
            rows = cursor.execute(sql).fetchall()
            print("SQL Result:")
            for row in rows:
                print(row)
            sql_result = str(rows)
        except Exception as e:
            print("SQL Error:\n" + str(e))
            sql_result = str(e)
        print("")
        prompt = (f"I asked a question \"{question}\" and here is a response to a SQL query that should answer it: \n{sql_result}\n"
                "Please provide a concise response to the question. Be quite brief. "
                "If there is an error, do not explain it, just do your best to answer the question.\n")
        response = get_ai_response(prompt)
        print("Response:\n" + response + "\n\n")

print("--------------------\nZero-shot questions\n--------------------\n")
ask_questions(one_shot=False)
print("--------------------\nOne-shot questions\n--------------------\n")
ask_questions(one_shot=True)

connection.commit()