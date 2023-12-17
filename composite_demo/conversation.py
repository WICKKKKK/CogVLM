import requests
import re
import streamlit as st

from dataclasses import dataclass
from enum import auto, Enum
from PIL.Image import Image
from PIL import ImageDraw
from streamlit.delta_generator import DeltaGenerator


class Role(Enum):
    """
    CogVLM | CogAgent Only have 2 roles: USER, ASSISTANT

    Represents the roles in a conversation, specifically for CogVLM and CogAgent applications.

    There are two roles available:
    - USER: The user of the system, typically the one asking questions or initiating conversation.
    - ASSISTANT: The system or AI assistant responding to the user's queries.

    Methods:
        get_message(self):
            Retrieves a Streamlit chat message component based on the role. For the USER role, it
            returns a chat message with the name "user" and user avatar. For the ASSISTANT role,
            it returns a chat message with the name "assistant" and assistant avatar.
    """

    USER = auto()
    ASSISTANT = auto()

    def get_message(self):

        match self.value:
            case Role.USER.value:
                return st.chat_message(name="user", avatar="user")
            case Role.ASSISTANT.value:
                return st.chat_message(name="assistant", avatar="assistant")
            case _:
                st.error(f'Unexpected role: {self}')


@dataclass
class Conversation:
    """
        Represents a single conversation turn within a dialogue.

        Attributes:
            role (Role): The role of the speaker in the conversation (USER or ASSISTANT).
            content (str): The textual content of the conversation turn.
            image (Image, optional): An optional image associated with the conversation turn.
            content_show (str, optional): The content to be displayed in the WebUI. This may differ
                from `content` if translation or other processing is applied.

        Methods:
            __str__(self) -> str:
                Returns a string representation of the conversation turn, including the role and content.

            show(self, placeholder: DeltaGenerator | None = None) -> str:
                Displays the conversation turn in the WebUI. If `placeholder` is provided, the content
                is shown in the specified Streamlit container. Otherwise, it uses the message style
                determined by the role.
    """

    role: Role = Role.USER
    content: str = ""
    image: Image | None = None
    content_show: str | None = None


    def __str__(self) -> str:
        print(self.role, self.content)
        match self.role:
            case Role.USER | Role.ASSISTANT:
                return f'{self.role}\n{self.content}'

    def show(self, placeholder: DeltaGenerator | None = None) -> str:
        """
        show in markdown formate
        """
        if placeholder:
            message = placeholder
        else:
            message = self.role.get_message()

        # for Chinese WebUI show
        if self.role == Role.USER:
            # show in Chinese and turn it to english
            # self.content = translate_baidu(self.content_show, source_lan="zh", target_lan="en")
            self.content = self.content_show
        if self.role == Role.ASSISTANT:
            # and turn it to Chinese and show
            # self.content_show = translate_baidu(self.content, source_lan="en", target_lan="zh")
            self.content_show = self.content

            self.content_show = self.content_show.replace('\n', '  \n')

        message.markdown(self.content_show)
        if self.image:
            message.image(self.image)


def preprocess_text(history: list[Conversation], ) -> str:
    """
        Prepares the conversation history for processing by concatenating the content of each turn.

        Args:
            history (list[Conversation]): The conversation history, a list of Conversation objects.

        Returns:
            str: A single string that concatenates the content of each conversation turn, followed by
            the ASSISTANT role indicator. This string is suitable for use as input to a text generation model.
    """

    prompt = ""
    for conversation in history:
        prompt += f'{conversation}'
    prompt += f'{Role.ASSISTANT}\n'
    return prompt


def postprocess_text(template: str, text: str) -> str:
    """
    Post-processes the generated text by incorporating it into a given template.

    Args:
        template (str): A template string containing a placeholder for the generated text.
        text (str): The generated text to be incorporated into the template.

    Returns:
        str: The template with the generated text replacing the placeholder.
    """
    quoted_text = f'"{text.strip()}"'
    return template.replace("<TASK>", quoted_text).strip()


# def postprocess_image(text: str, img: Image) -> (str, Image):
#     """
#        Processes the given text to identify and draw bounding boxes on the provided image.
#
#        This function searches for patterns in the text that represent coordinates for bounding
#        boxes and draws rectangles on the image at these coordinates. Each box is drawn in a
#        different color for distinction.
#
#        Args:
#            text (str): The text containing bounding box coordinates in a specific pattern.
#            img (Image): The image on which to draw the bounding boxes.
#
#        Returns:
#            tuple[str, Image]: The processed text with additional annotations for each bounding
#            box, and the image with the drawn bounding boxes.
#        """
#     colors = ["red", "green", "blue", "yellow", "purple", "orange"]
#     pattern = r"\[\[(\d+),(\d+),(\d+),(\d+)\]\]"
#     matches = re.findall(pattern, text)
#     unique_matches = []
#     draw = ImageDraw.Draw(img)
#     if matches == []:
#         return text, None
#
#     for i, coords in enumerate(matches):
#         if coords not in unique_matches:
#             unique_matches.append(coords)
#             scaled_coords = (
#                 int(float(coords[0]) * 0.001 * img.width),
#                 int(float(coords[1]) * 0.001 * img.height),
#                 int(float(coords[2]) * 0.001 * img.width),
#                 int(float(coords[3]) * 0.001 * img.height)
#             )
#             draw.rectangle(scaled_coords, outline=colors[i % len(colors)], width=3)
#             color_text = f"(in {colors[i % len(colors)]} box)"
#             text = text.replace(f"[[{','.join(coords)}]]", f"[[{','.join(coords)}]]{color_text}", 1)
#     return text, img


def postprocess_image(text: str, img: Image) -> (str, Image):
    colors = ["red", "green", "blue", "yellow", "purple", "orange"]

    pattern = r"\[\[(.*?)\]\]"
    matches = re.findall(pattern, text)
    if not matches:
        return text, None
    processed = set()
    draw = ImageDraw.Draw(img)
    for match in matches:
        positions = match.group(1).split(';')
        boxes = [tuple(map(int, pos.split(','))) for pos in positions if pos.replace(',', '').isdigit()]

        for i, box in enumerate(boxes):
            if box not in processed:
                processed.add(box)


                scaled_box = (
                    int(box[0] * 0.001 * img.width),
                    int(box[1] * 0.001 * img.height),
                    int(box[2] * 0.001 * img.width),
                    int(box[3] * 0.001 * img.height)
                )
                draw.rectangle(scaled_box, outline=colors[i % len(colors)], width=3)
                color_text = f"(in {colors[i % len(colors)]} box)"
                text = text.replace(f"[[{','.join(map(str, box))}]]", f"[[{','.join(map(str, box))}]]{color_text}", 1)

    return text, img

def translate_baidu(translate_text, source_lan, target_lan):
    """
        Translates text using Baidu's translation service. (if you are not use English)

        This function sends a request to the Baidu translation API to translate the provided text
        from the source language to the target language.

        Args:
            translate_text (str): The text to be translated.
            source_lan (str): The source language code (e.g., "en" for English).
            target_lan (str): The target language code (e.g., "zh" for Chinese).

        Returns:
            str: The translated text. Returns "error" in case of an exception.
        """
    url = "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token="
    headers = {'Content-Type': 'application/json'}
    payload = {
        'q': translate_text,
        'from': source_lan,
        'to': target_lan
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        result = r.json()
        final_translation = ''

        for item in result['result']['trans_result']:
            final_translation += item['dst'] + '\n'
    except Exception as e:
        print(e)
        return "error"
    return final_translation