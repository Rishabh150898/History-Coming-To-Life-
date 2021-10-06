import torch
import pyttsx3
from flask import Flask, request, render_template, jsonify
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField
import os


app = Flask(__name__,static_folder="/")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test2.db'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
sqldb = SQLAlchemy()

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2))
    name = db.Column(db.String(50))

class Form(FlaskForm):
    state = SelectField('state', choices=[('7 NCERT', '7 NCERT'), ('8 NCERT', '8 NCERT'), ('9 NCERT', '9 NCERT'), ('10 NCERT', '10 NCERT'), ('7 SSC', '7 SSC'), ('8 SSC', '8 SSC'), ('9 SSC', '9 SSC'), ('10 SSC', '10 SSC')])
    city = SelectField('city', choices=[])

finetunedmodel='bert-large-uncased-whole-word-masking-finetuned-squad'

@app.route('/', methods=['GET', 'POST'])
def my_form():
    form = Form()
    form.city.choices = [(city.id, city.name) for city in City.query.filter_by(state='7 NCERT').all()]
    return render_template('home.html', form=form)

@app.route('/city/<state>')
def city(state):
    cities = City.query.filter_by(state=state).all()

    cityArray = []

    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.name
        cityArray.append(cityObj)

    return jsonify({'cities' : cityArray})

@app.route('/result', methods=['GET', 'POST'])
def my_form_post():
    if request.form['btn'] == 'Search':
        form1 = Form()
        city = City.query.filter_by(id=form1.city.data).first()
        text=city.name
        print(text)
    else:
        text = request.form['u']
#start loading
    if text == 'Jawaharlal Nehru':
        text1 = "<pad> Jawaharlal Nehru was an Indian independence activist and, subsequently, the first Prime Minister of India. He served as India's Prime Minister from 1947 until his death in 1964. Nehru was also known as Pandit Nehru due to his roots with the Kashmiri Pandit community. In India, his birthday is celebrated as Children's Day Under Nehru's leadership, the Congress emerged as a catch-all party, dominating national and state-level politics and winning consecutive elections in 1951, 1957, and 1962. He remained popular with the people of India in spite of political troubles in his final years and failure of leadership during the 1962 Sino-Indian War.</s>"
        text2 = text1[6:-4]
    else:
        text1 = "<pad> Mohandas Karamchand Gandhi (; 2 October 1869 – 30 January 1948) was an Indian lawyer, anti-colonial nationalist and political ethicist who employed nonviolent resistance to lead the successful campaign for India's independence from British rule. Gandhi trained in law at the Inner Temple, London, and was called to the bar at age 22 in June 1891. Gandhi is commonly, though not formally, considered the Father of the Nation in India and was commonly called Bapu (Gujarati: endearment for father, papa) Gandhi's birthday, 2 October, is commemorated in India as Gandhi Jayanti, a national holiday, and worldwide as the International Day of Nonviolence.</s>"
        text2 = text1[6:-4]


    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    engine.save_to_file(text2, 'speech.mp3')
    engine.runAndWait()

#stop loading
    return render_template('video1.html',text3=text2, name=text)

model = BertForQuestionAnswering.from_pretrained(finetunedmodel)
tokenizer = BertTokenizer.from_pretrained(finetunedmodel)

@app.route('/voice', methods=['Post'])
def voice_ai():
    req=request.get_json()
    question=str(list(req.values())[0])

    def question_answer(question, text):
        model = BertForQuestionAnswering.from_pretrained(finetunedmodel)
        tokenizer = BertTokenizer.from_pretrained(finetunedmodel)
        # tokenize question and text as a pair
        input_ids = tokenizer.encode(question, text)

        # string version of tokenized ids
        tokens = tokenizer.convert_ids_to_tokens(input_ids)

        # segment IDs
        # first occurence of [SEP] token
        sep_idx = input_ids.index(tokenizer.sep_token_id)
        # number of tokens in segment A (question)
        num_seg_a = sep_idx + 1
        # number of tokens in segment B (text)
        num_seg_b = len(input_ids) - num_seg_a

        # list of 0s and 1s for segment embeddings
        segment_ids = [0] * num_seg_a + [1] * num_seg_b
        assert len(segment_ids) == len(input_ids)

        # model output using input_ids and segment_ids
        output = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))

        # reconstructing the answer
        answer_start = torch.argmax(output.start_logits)
        answer_end = torch.argmax(output.end_logits)
        if answer_end >= answer_start:
            answer = tokens[answer_start]
            for i in range(answer_start + 1, answer_end + 1):
                if tokens[i][0:2] == "##":
                    answer += tokens[i][2:]
                else:
                    answer += " " + tokens[i]

        if answer.startswith("[CLS]"):
            answer = "Unable to find the answer to your question."

        question_answer.response = answer.capitalize()


    text = """
    Jawaharlal Nehru (/ˈneɪru, ˈnɛru/;[1] Hindi: [ˈdʒəʋaːɦərˈlaːl ˈneːɦru] (About this soundlisten); 14 November 1889 – 27 May 1964) was an Indian independence activist and, subsequently, the first prime minister of India. Considered as one of the greatest statesmen of India[2] and of the twentieth century,[3] he was a central figure in Indian politics both before and after independence. He emerged as an eminent leader of the Indian independence movement, serving India as Prime Minister from its establishment in 1947 as an independent nation, until his death in 1964. He was also known as Pandit Nehru due to his roots with the Kashmiri Pandit community, while Indian children knew him better as Chacha Nehru (Hindi: Uncle Nehru).[4][5]

The son of Swarup Rani and Motilal Nehru, a prominent lawyer and nationalist statesman, Nehru was a graduate of Trinity College, Cambridge and the Inner Temple, where he trained to be a barrister. Upon his return to India, he enrolled at the Allahabad High Court and took an interest in national politics, which eventually replaced his legal practice. 
    """

    question_answer(question, text)


    print(question)

    return jsonify({"response": question_answer.response })


@app.route('/contact')
def team():
    return render_template('contact.html')


@app.route('/about')
def team1():
    return render_template('about.html')

if __name__ == "__main__":
    app.run()