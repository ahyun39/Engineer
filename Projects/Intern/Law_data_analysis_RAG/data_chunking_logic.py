# -*- coding: utf-8 -*-

import json
import pandas as pd
from collections import defaultdict
from configparser import ConfigParser


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_s2(data):
    # data columns : ['doc_id', 'full_title', 'doc_title', 'chunks', 'doc_url']
    cut_s2, table, table_idx = [], [], 0

    for item in data:
        chunks, doc_title, doc_url = item['chunks'], item['doc_title'], item['doc_url']
        title, s1, s2 = "", "", ""  # chunk_title
        tag, chunk_list = [], []
        if "onhunqna" not in doc_url:
            for chunk in chunks:
                chunk_tag, chunk_content = map(str, chunk.split(" _ "))

                if chunk_content:
                    if chunk_tag in ["s1", "s2"] and chunk_content[0] == "※":
                        tag.append('s3')
                        chunk_list.append(chunk_content)

                    else:
                        if chunk_tag == "s1":
                            if chunk_list:
                                cut_s2.append(
                                    [item['doc_id'], title or s1 or doc_title, tag, chunk_list, item['doc_url']])
                            else:
                                if s1 and s2:
                                    cut_s2.append([item['doc_id'], s1, tag, [s2], item['doc_url']])
                            s1, title, s2 = chunk_content, "", ""
                            tag, chunk_list = [], []

                        elif chunk_tag == "s2":
                            if chunk_list:
                                cut_s2.append(
                                    [item['doc_id'], title or s1 or doc_title, tag, chunk_list, item['doc_url']])
                            title = f'{s1} : {chunk_content}'
                            tag, chunk_list = [], []
                            s2 = chunk_content

                        elif chunk_tag not in ["s1", "s2"]:
                            if chunk_tag[0] != "i":
                                if "table" in chunk_content:
                                    chunk_tag = "table"
                                    table.append([f"TABLE_{table_idx}", chunk_content])
                                    chunk_content = f'TABLE_{table_idx}'
                                    table_idx += 1
                                    cut_s2.append(
                                        [item['doc_id'], f'{title or s1 or doc_title} (table)', "TABLE", [chunk_content],
                                         item['doc_url']])
                                else:
                                    tag.append(chunk_tag)
                                    chunk_list.append(chunk_content)
            if chunk_list:
                cut_s2.append([item['doc_id'], title or s1 or doc_title, tag, chunk_list, item['doc_url']])
            else:
                if chunk_tag[0] != "i" and chunk_tag != "table":
                    if s1 and s2:
                        cut_s2.append([item['doc_id'], s1, tag, [s2], item['doc_url']])
    return cut_s2, table


def split_by_length(data, threshold):
    over_threshold = [item for item in data if len(' '.join(item[3])) > threshold]
    under_threshold = [item for item in data if len(' '.join(item[3])) <= threshold]

    return over_threshold, under_threshold


def replace_tags(data):
    # columns : ['doc_id','title','tag','chunks','doc_url']
    relace_tag_data = []
    for item in data:
        tags = item[2]
        new_tag, now_tag = "s3", "s0"  # 변수 초기화
        for i in range(len(tags)):
            if (tags[i] == "r2" and now_tag != tags[i]) or (
                    tags[i] == "t2" and new_tag == "s3" and now_tag[0] not in ["r", "t"]):
                new_tag, now_tag = "s3", tags[i]
                tags[i] = new_tag
            elif (tags[i] in ["r2", "t2"] and now_tag == tags[i]):
                new_tag, now_tag = "s8", tags[i]
                tags[i] = new_tag
            elif (tags[i][0] in ["r", "t"]):
                new_tag, now_tag = "s8", tags[i]
                tags[i] = new_tag
            elif (tags[i] in ["s1", "s2", "s3"]):
                new_tag, now_tag = "s3", tags[i]
        relace_tag_data.append(item)

    return relace_tag_data


def group_by_s3(data):
    # columns : ['doc_id','title','tag','chunks','doc_url']
    cut_s3 = []

    for item in data:
        doc_id, title, tags, chunks, doc_url = item
        title_idx, tag, chunk_list = 0, [], []

        for doc_tag, content in zip(tags, chunks):
            if content:
                if doc_tag == "s3":
                    if chunk_list:
                        cut_s3.append([doc_id, f'{title} - {title_idx:03}', tag, chunk_list, doc_url])
                        title_idx += 1
                        tag, chunk_list = [], []
                    tag.append(doc_tag)
                    chunk_list.append(content)
                else:
                    tag.append(doc_tag)
                    chunk_list.append(content)
        cut_s3.append([doc_id, f'{title} - {title_idx:03}', tag, chunk_list, doc_url])

    return cut_s3


def split_long_chunks(data, threshold):
    # columns : ['doc_id', 'chunk_title', 'chunk_content', 'doc_url']
    chunk_list = []
    for item in data:
        doc_id, title, _, chunks, doc_url = item
        chunk_idx, chunk_content = 1, ""
        sentence_list = []
        for chunk in chunks:
            if len(chunk_content) + len(chunk) > threshold:
                if chunk_content:
                    chunk_list.append([doc_id, f'{title} - {chunk_idx:03}', sentence_list, doc_url])
                    chunk_idx += 1
                chunk_content = chunk
                sentence_list = [chunk]
            else:
                chunk_content += (" " + chunk)
                sentence_list.append(chunk)
        chunk_list.append([doc_id, f'{title} - {chunk_idx:03}', sentence_list, doc_url])
    return chunk_list


def merge_data(data, data2, data3, missing_data):
    # columns : ['doc_id' , 'url', 'chunk_id', 'chunk_title', 'chunk_content', 'sentence_split']
    merged_data = [
                      [item[0], item[4], '', item[1], ' '.join(item[3]).strip(), item[3]] for item in data
                  ] + [
                      [item[0], item[4], '', item[1], ' '.join(item[3]).strip(), item[3]] for item in data2
                  ] + [
                      [item[0], item[3], '', item[1], ' '.join(item[2]), item[2]] for item in data3
                  ]

    merged_data.extend(list(item.values()) for item in missing_data)  # 텍스트가 이미지 처리되어 누락된 데이터 처리

    unique_merged_data = list({(item[3], item[4]): item for item in merged_data}.values())
    unique_merged_data.sort(key=lambda x: (x[0], x[3]))
    return unique_merged_data


def remove_title_suffix(data):
    return [[item[0], item[1], item[2], item[3].split(" - ")[0], item[4], item[5]] for item in data]


def add_idx(data):
    # columns : ['doc_id' , 'url', 'chunk_id', 'chunk_title', 'chunk_content', 'sentence_split']
    title_index, title_counts, doc_index = defaultdict(int), defaultdict(int), defaultdict(int)

    for item in data:
        title_counts[item[0] + item[3]] += 1

    for item in data:
        doc_id, chunk_title = item[0], item[3]
        doc_chunk_title = doc_id + chunk_title

        title_index[doc_chunk_title] += 1
        index = title_index[doc_chunk_title]
        total_count = title_counts[doc_chunk_title]  # 같은 chunk_title을 가진 문서 전체 개수

        doc_index[doc_id] += 1
        item[2] = f"{doc_id}_{doc_index[doc_id]:04}"  # chunk_idx

        if total_count > 1:
            item[3] = f"{chunk_title} {index}/{total_count}"  # chunk_title
            index += 1

    return data


def create_doc_title_dict(file_name):
    # document title 추가하기 위한 딕셔너리 생성 함수
    data = load_json(file_name)
    return {item['doc_id']: item['full_title'] for item in data}


# 백문백답 처리
def add_qna(qna_file_name, f_data, title_dict, output_file):
    # input info
    ## qna_file_name : 'qna_data.json' - 백문백답 데이터
    ## f_data : 로직대로 chunking 한 데이터
    ## title_dict : create_doc_title_dict로 생성한 title dictionary
    data_qna = load_json(qna_file_name)  # content_d에 있는 데이터 중 백문백답 데이터만 가져옴.

    qna_dict = defaultdict(list)  # data_qna 에 있는 전체 백문백답을 담은 딕셔너리
    for item in data_qna:
        doc_id = item['doc_id']
        qna_dict[doc_id].append([
            item['doc_url'], doc_id, f"{doc_id}_{item['con_id']:04}", doc_id,
            f"{doc_id}_{item['con_id']:04}", item['doc_title'], item['title'], item['content'].strip(),
            item['content_split']
        ])

    # columns : ['url', 'parent_id', 'id', 'orgdoc_id', 'chunk_id', 'document_title', 'chunk_title', 'chunk_content', 'sentence_split']
    add_qna_data = []  # f_data에 백문백답 추가한 데이터

    for data in f_data:
        doc_id, url = data[0], data[1]
        add_qna_data.append([
            url, doc_id, data[2], doc_id, data[2], title_dict[data[0]], data[3], data[4], data[5]
        ])

    add_qna_data.extend(qna for item in list(qna_dict.values()) for qna in item)

    df = pd.DataFrame(add_qna_data,
                      columns=['url', 'parent_id', 'id', 'orgdoc_id', 'chunk_id', 'document_title', 'chunk_title',
                               'chunk_content', 'sentence_split'])
    df.to_json(output_file, force_ascii=False, orient='records', indent=4)


def main():
    config = ConfigParser()
    config.read('conf.ini')

    file_name = config['chunking_logic']['crawling_data']
    qna_file_name = config['chunking_logic']['qna_file_name']
    threshold = int(config['chunking_logic']['threshold'])
    output_file = config['chunking_logic']['output_file']
    missing_data = json.loads(config['chunking_logic']['missing_data'])

    data = load_json(file_name)

    # 1. s2로 묶기
    cut_s2, table = process_s2(data)
    # 2. 글자수 700 넘어가는 내용 서치
    s2_over_threshold, s2_under_threshold = split_by_length(cut_s2, threshold)
    # 3. r, t인 tag 치환
    data = replace_tags(s2_over_threshold)
    # 4. s3로 묶기
    cut_s3 = group_by_s3(data)
    # 5. 글자수 700 넘어가는 내용 서치
    s3_over_threshold, s3_under_threshold = split_by_length(cut_s3, threshold)
    # 6. 글자수 기준으로 문장단위로 묶기
    data = split_long_chunks(s3_over_threshold, threshold)

    merged_data = merge_data(s2_under_threshold, s3_under_threshold, data, missing_data)  # 로직대로 나눈 데이터 합치기
    data = remove_title_suffix(merged_data)
    f_data = add_idx(data)  # 같은 문서 표시

    title_dict = create_doc_title_dict(file_name)
    add_qna(qna_file_name, f_data, title_dict, output_file)  # 백문백답 데이터 추가


if __name__ == '__main__':
    main()