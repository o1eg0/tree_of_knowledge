import re

import spacy
import torch
import wordninja
from transformers import BertTokenizer, BertForNextSentencePrediction
from wordfreq import zipf_frequency

nlp = spacy.load("en_core_web_sm")
nlp.max_length = 9000000


class NoiseCleaner:
    def __init__(self, text: str):
        self.text = text
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertForNextSentencePrediction.from_pretrained('bert-base-uncased')
        self.pos_tags_to_remove = {'ADP', 'DET', 'CCONJ', 'PART', 'AUX', 'SPACE'}

    def remove_urls(self):
        """Удаляет ссылки из текста."""
        url_pattern = r'https?://\S+|www\.\S+'
        self.text = re.sub(url_pattern, '', self.text)

    def remove_single_letter_spaces(self):
        """Удаляет подстроки, состоящие из одной буквы между пробелами."""
        self.text = re.sub(r' [a-zA-ZА-Яа-я] ', '', self.text)

    def remove_code_parts(self):
        """Удаляет части кода в виде (cid: XX) из текста."""
        code_pattern = r'\(cid:\s*\d+\)'
        self.text = re.sub(code_pattern, '', self.text)

    def remove_short_lines(self):
        """Удаляет строки, которые короче или равны 20 символам и не содержат слов длиннее 3 букв."""
        # Разделяем текст на строки
        lines = self.text.split('\n')
        filtered_lines = []

        for line in lines:
            # Проверяем длину строки и наличие слов длиннее 3 букв
            if len(line) > 20 or any(len(word) > 3 for word in line.split()):
                filtered_lines.append(line)

        # Соединяем отфильтрованные строки обратно в текст
        self.text = '\n'.join(filtered_lines)

    def split_words(self):
        # self.text = ' '.join(self.spell(self.text))
        self.text = ' '.join(wordninja.split(self.text))

    def filter_text_by_zipf(self, min_zipf=3.0):
        words = self.text.split()
        # Фильтрация слов на основе их Zipf-оценки
        filtered_words = [word for word in words if zipf_frequency(word, 'en') >= min_zipf]
        return ' '.join(filtered_words)

    def remove_single_letters_except_i(self):
        pattern = r'\b[^iI\s]\b'
        self.text = re.sub(pattern, '', self.text)

    def remove_special_chars_and_ligatures(self):
        """Удаляет специальные символы и лигатуры."""
        ligatures_replacements = {
            'ﬀ': 'ff',
            'ﬁ': 'fi',
            'ﬂ': 'fl',
            'ﬃ': 'ffi',
            'ﬄ': 'ffl',
        }

        for ligature, replacement in ligatures_replacements.items():
            self.text = self.text.replace(ligature, replacement)

        self.text = re.sub(r'[\\/]', ' ', self.text)
        self.text = re.sub(r'[^а-яА-Яa-zA-Z0-9 \n.’]', '', self.text)

    def remove_non_informative_lines(self):
        """Удаляет строки, не содержащие важного контекста."""
        important_keywords = {'isbn', 'university', 'department', 'institute', 'professor', 'dr.', 'ph.d', 'm.sc'}
        lines = self.text.split('\n')
        filtered_lines = []

        for line in lines:
            # Условие для сохранения строки: содержит ключевое слово или более 3 слов
            if len(set(line.lower().split()) & important_keywords) > 0 or len(line.split()) > 3:
                filtered_lines.append(line)

        self.text = '\n'.join(filtered_lines)

    def merge_hyphenated_words(self):
        """Объединяет слова, разделённые дефисом и перенесённые на новую строку."""
        self.text = re.sub(r'-(\n|\r|\r\n)([a-zA-Zа-яА-Я])', r'\2', self.text)

    def remove_extra_spaces(self):
        """Удаляет лишние пробелы."""
        self.text = re.sub(r' +', ' ', self.text)

    def fix_newlines(self):
        """Заменяет переводы строк на пробелы."""
        lines = self.text.split('\n')
        lines = [line.strip() for line in lines]
        self.text = '\n'.join(lines)
        self.text = re.sub(r'\n+', '\n', self.text)

    def replace_number_sequences(self):
        """Обновленная обработка числовых последовательностей."""
        # Пример сохранения годов и ISBN
        # self.text = re.sub(r'\b(19|20)\d{2}\b', r'YEAR\g<0>', self.text)  # Годы
        self.text = re.sub(r'\bISBN[- ]?(\d{10}|\d{13})\b', r'ISBN \g<1>', self.text)  # ISBN

    def maintain_structure(self):
        """Сохранение структуры списков и абзацев."""
        self.text = re.sub(r'\n+', '\n', self.text)  # Уплотняем множественные переводы строк
        self.text = re.sub(r'(\n[•\-]\s*)', r'\g<1>', self.text)  # Маркированные списки

    def remove_isolated_numbers(self):
        """Удаляет строки, содержащие только число."""
        self.text = re.sub(r'^\d+\s*$', '', self.text, flags=re.MULTILINE)

    def remove_lines_without_letters(self):
        """Удаляет строки, не содержащие буквенных символов."""
        self.text = '\n'.join(line for line in self.text.split('\n') if re.search('[a-zA-Zа-яА-Я]', line))

    def compress_numbered_lists(self):
        """Сжимает списки, где каждый элемент начинается с числа."""
        self.text = re.sub(r'(?<=\n)\d+\s*(\.\s*)?([A-Za-zА-Яа-я].+?)(?=\n\d+\s*(\.\s*)?[A-Za-zА-Яа-я])', r'\2; ',
                           self.text)

    def remove_roman_numerals(self):
        """Заменяет римские числа на 'NUMBER1'."""
        roman_numerals_pattern = r'\b(?=[MDCLXVImdclxvi]+\b)(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})|M{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3}))\b'
        self.text = re.sub(roman_numerals_pattern, '', self.text)

    def evaluate_coherence(self, context, sentence):
        """Оценивает, насколько логично предложение является продолжением контекста."""
        inputs = self.tokenizer.encode_plus(context, sentence, return_tensors='pt', max_length=512, truncation=True)

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        probs = torch.softmax(logits, dim=1)
        coherent_score = probs[0][0].item()

        return coherent_score

    def remove_lists(self):
        """Удаляет списки, соответствующие определённому паттерну."""
        pattern = r'^\d+(\.\d+)?\s.*$'
        # Разделяем текст на строки и применяем регулярное выражение к каждой строке
        # Оставляем строки, которые не соответствуют паттерну
        self.text = '\n'.join(line for line in self.text.split('\n') if not re.match(pattern, line))

    def evaluate_and_filter_sentences(self, coherence_threshold=0.5):
        """Оценивает и фильтрует предложения на основе их осмысленности."""
        sentences = self.text.split('\n')
        filtered_text = []
        previous_sentence = None

        for sentence in sentences:
            if previous_sentence is not None:
                # Оцениваем осмысленность текущего предложения в контексте предыдущего
                coherence_score = self.evaluate_coherence(previous_sentence, sentence)
                if coherence_score >= coherence_threshold:
                    filtered_text.append(sentence)
            else:
                # Если нет предыдущего предложения, просто добавляем текущее предложение
                filtered_text.append(sentence)

            previous_sentence = sentence

        self.text = '\n'.join(filtered_text)

    def replace_newlines(self):
        """Заменяет переводы строк на пробелы."""
        self.text = re.sub(r'\n+', ' ', self.text)

    def remove_letter_dot_spaces(self):
        """Удаляет все подстроки вида ' Буква. ', отделенные пробелами."""
        self.text = re.sub(r'\s+[A-Za-zА-Яа-я]\.\s+', ' ', self.text)

    def remove_dot_sequences(self):
        """Удаляет последовательности точек, включая те, что разделены пробелами."""
        # Сначала удаляем пробелы между точками, чтобы привести последовательности к виду "...."
        self.text = re.sub(r'\.\s+\.', '..', self.text)
        # Затем удаляем последовательности из двух и более точек
        self.text = re.sub(r'\.{2,}', '', self.text)

    def process(self, coherence_threshold=0.5):
        """Выполняет полную обработку текста."""
        self.merge_hyphenated_words()
        self.remove_urls()
        self.remove_code_parts()
        self.remove_special_chars_and_ligatures()
        self.fix_newlines()
        self.remove_extra_spaces()

        self.replace_number_sequences()
        self.remove_roman_numerals()
        # self.replace_roman_numerals_with_number1()
        # self.replace_dots_sequences()
        # self.replace_number1_sequences()
        self.remove_letter_dot_spaces()

        self.remove_letter_dot_spaces()
        self.remove_single_letter_spaces()
        self.maintain_structure()
        self.remove_extra_spaces()

        self.remove_isolated_numbers()
        self.compress_numbered_lists()

        self.remove_non_informative_lines()
        self.remove_lines_without_letters()
        self.remove_reference_lines()
        self.remove_lists()
        self.remove_short_lines()
        # self.evaluate_and_filter_sentences(coherence_threshold)
        self.fix_newlines()
        self.remove_dot_sequences()
        self.text = re.sub(r'[^а-яА-Яa-zA-Z \n.]', '', self.text)
        self.normalize_text()
        self.text = re.sub(r'[^а-яА-Яa-zA-Z \n]', '', self.text)
        self.text = self.text.lower().strip()
        self.remove_extra_spaces()
        self.remove_single_letter_spaces()
        # self.replace_newlines()
        # self.remove_extra_spaces()
        self.split_words()
        self.normalize_text()
        # self.filter_text_by_zipf()

        self.remove_single_letters_except_i()
        self.remove_extra_spaces()
        return self.text.strip()

    def lemmatize_fragment(self, fragment):
        """Лемматизирует отдельный фрагмент текста."""
        corrected_fragment = fragment
        doc = nlp(corrected_fragment)
        return ' '.join(token.lemma_ for token in doc if token.pos_ not in self.pos_tags_to_remove)

    def normalize_text(self):
        """Нормализует весь текст, обрабатывая каждый фрагмент отдельно."""
        # Разбиваем текст на фрагменты по точке в конце строки
        fragments = re.split(r'\.\n+', self.text)
        # print(self.lemmatize_fragment(fragments[2]))
        # exit(0)
        lemmatized_fragments = [self.lemmatize_fragment(fragment) for fragment in fragments]

        # Соединяем обработанные фрагменты обратно в единый текст
        self.text = '\n'.join(lemmatized_fragments)

    def remove_reference_lines(self):
        """Удаляет строки, представляющие собой ссылки или метки для чтения."""
        patterns_to_remove = [
            r'^see\s',  # Строки, начинающиеся с "see"
            r'w\.r\.t\.',  # Строки, содержащие "w.r.t."
            r'\smodel\s',  # Строки, содержащие " model "
            r'\slogic\s',  # и так далее для других ключевых слов...
            r'\saxiom\s',
            r'\sclosure\s',
            r'^\w+\s+\d+',  # Строки, начинающиеся с одного слова, за которым идут числа
            r'\d+\s+\d+',  # Строки, содержащие только числа
        ]
        combined_pattern = '(' + '|'.join(patterns_to_remove) + ')'
        self.text = '\n'.join(
            line for line in self.text.split('\n') if not re.search(combined_pattern, line, re.IGNORECASE))


if __name__ == "__main__":
    path = '0000638_The_Description_Logi.txt'
    with open(path, 'r', encoding='utf-8') as file:
        sample_text = file.read()

    cleaner = NoiseCleaner(sample_text)
    cleaned_text = cleaner.process()

    new_path = path.replace('.txt', '.processed')
    with open(new_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)
