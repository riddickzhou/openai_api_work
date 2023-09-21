import openai
import json

openai.api_key = ""


def get_results(input_messages, temperature=0):
    try:
        response = openai.ChatCompletion.create(
            model = 'gpt-4',
            messages=input_messages,
            temperature=temperature,
            max_tokens=5000
        )
        result = response.choices[0].message['content']
    except:
        result = 'Error'
    return result


def read_data(text_file, n=1):
    # read data
    with open(text_file, 'r', encoding='utf8') as f:
        raw_lines = f.readlines()
        if n == -1:
            raw_lines = raw_lines
        else:
            raw_lines = raw_lines[:n]
        lines = [json.loads(i.strip()) for i in raw_lines]
    outputs = []
    # reformat
    for i in lines:
        outputs.append(i['prompt'].strip()+'-|-'+i['response'].strip())
    return outputs


def build_messages(input_data):
    messages = []
    for i in input_data:
        cur_mess = []
        # add instruction
        cur_mess.append(
            {
            "role": "system",
            "content":
                """下面我会输入一些问题以及对应的答案，问题与答案用'-|-'分隔。任务是判断答案是否正确。如果正确返回'YES'，并以专家的口吻作答一遍。如果不正确，返回'NO'，指出存在的问题，并用中文重新生成正确答案。"""
        },
        )
        # add data
        cur_mess.append(
            {
                "role": "user",
                "content": i
            },
        )
        messages.append(cur_mess)
    return messages


if __name__ == "__main__":
    iter_per_file = 100
    outputs = read_data(
        'C:\\Users\\Ge Zhang\\Desktop\\chatGPT\\data\\time_space_evol_web_results_0915.json',
        n=-1
    )
    f = None
    messages = build_messages(outputs)
    for idx, mess in enumerate(messages):
        if idx%iter_per_file == 0:
            if f:
                f.close()
            print('opening file result_try_correct_part_%d.txt'%(idx//iter_per_file))
            f = open('C:\\Users\\Ge Zhang\\Desktop\\chatGPT\\data\\result_try_correct_part_%d.txt'%(idx//iter_per_file), 'a', encoding='utf-8')
        res = get_results(mess)
        f.write('*** NO.%d ***\n'%(idx))
        f.write('Q: ' + mess[1]['content'].split('-|-')[0] + '\n')
        f.write('our_A: ' + mess[1]['content'].split('-|-')[1] + '\n')
        f.write('=======\n')
        f.write('GPT4_A: ' + res + '\n')
        f.write('\n---------------------------------------\n\n')
    f.close()
