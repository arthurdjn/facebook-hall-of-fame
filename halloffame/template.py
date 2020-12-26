# Creation: Saturday December 5th 2020
# Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin


import re
import unidecode
from datetime import datetime


def apply_font(message, font="bold"):
    """Change the font of a string text.

    Args:
        message (str): Message to change the font.
        font (str, optional): Font to use. Availbale options are within ``{"bold", "italic", "serif"}``
            To use a combination (e.g. serif and italic), separate the name with a dash (e.g. ``"italic-serif"``). 
            Defaults to "bold".

    Returns:
        str
        
    Example:
        >>> apply_font("This is bold", font="bold")
            '𝗧𝗵𝗶𝘀 𝗶𝘀 𝗯𝗼𝗹𝗱'
        >>> apply_font("This is italic serif", font="italic-serif")
            '𝑇ℎ𝑖𝑠 𝑖𝑠 𝑖𝑡𝑎𝑙𝑖𝑐 𝑠𝑒𝑟𝑖𝑓'
    """
    ALPHABET = "abcdefghijklmnopqrstuvwyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    FONT = ALPHABET
    
    fonts_options = set(font.lower().split("-"))
    if fonts_options == {"bold"}:
        FONT = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    elif fonts_options == {"bold", "serif"}:
        FONT = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
    elif fonts_options == {"italic"}:
        FONT = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
    elif fonts_options == {"italic", "serif"}:
        FONT = "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"
    elif fonts_options == {"italic", "bold"}:
        FONT = "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙮𝙯𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
    elif fonts_options == {"bold", "italic", "serif"}:
        FONT = "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"

    message = unidecode.unidecode(message)
    new_message = ""
        
    for letter in message:
        if letter in ALPHABET:
            new_message += FONT[ALPHABET.index(letter)]
        else:
            new_message += letter

    return new_message


def apply_fonts_template(template):
    """Apply fonts in a template. A template is a long string element, containing delimiters where the fonts should be applied.
    This is usefull to apply multiple fonts in the same text.
    The delimiters are in the format: ``<<MY-FONT-TYPE>>my text with another font<<MY-FONT-TYPE>>`` where ``MY-FONT-TYPE`` is
    a combination of ``{"BOLD", "ITALIC", "SERIF"}`` (e.g. ``<<BOLD-SERIF>>my bold serif text<<BOLD-SERIF>>``)

    Args:
        template (str): Template where the font will be applied.
        
    Returns:
        str
        
    Example:
        >>> template = "<<BOLD>>This is a bold title<<BOLD>>\n\n<<ITALIC-SERIF>>A sub menu<<ITALIC-SERIF>>\n\n\nSome content."
        >>> apply_fonts_template(template)
            '𝗧𝗵𝗶𝘀 𝗶𝘀 𝗮 𝗯𝗼𝗹𝗱 𝘁𝗶𝘁𝗹𝗲\n\n𝐴 𝑠𝑢𝑏 𝑚𝑒𝑛𝑢\n\n\nSome content.'
    """
    def preprocess(string, font):
        return string.replace(f"<<{font.upper()}>>", "").replace(f"<<{font.upper()}>>", "")    
    
    FONTS = ["bold", "italic", "bold-italic", "bold-serif", "italic-serif", "bold-italic-serif"]
    for font in FONTS:
        template = re.sub(f"<<{font.upper()}>>(.*)<<{font.upper()}>>", lambda restring: apply_font(preprocess(restring.group(0), font=font), font=font), template)
    return template


def apply_stats_template(template, top_stats):   
    """Apply statistics template. Available keywords are:
    * :attr:`POST-COUNT` : The cumulative sum of posts.
    * :attr:`POST-REACTION-COUNT` : The cumulative sum of post reactions.
    * :attr:`BEST-POST-REACTION` : The posts with the highest reactions.
    * :attr:`COMMENT-COUNT` : The cumulative sum of comments.
    * :attr:`COMMENT-REACTION-COUNT` : The cumulative sum of comments reactions.
    * :attr:`BEST-COMMENT-REACTION` : The comments with the highest reactions.
    * :attr:`REPLY-COUNT` : The cumulative sum of replies.
    * :attr:`REPLY-REACTION-COUNT` : The cumulative sum of replies reactions.
    * :attr:`BEST-REPLY-REACTION` : The replies with the highest reactions.
    * :attr:`COMMENT-REPLY-COUNT` : The cumulative sum of replies and comments.
    * :attr:`REACTION-COUNT` : The cumulative sum of reactions.
    * :attr:`REACTION-AHAH` : The cumulative sum of "AHAH" reactions.
    * :attr:`REACTION-LOVE` : The cumulative sum of "LOVE" reactions.
    * :attr:`REACTION-CARE` : The cumulative sum of "CARE" reactions.
    * :attr:`REACTION-WOW` : The cumulative sum of "WOW" reactions.
    * :attr:`REACTION-SAD` : The cumulative sum of "SAD" reactions.
    * :attr:`REACTION-ANGER` : The cumulative sum of "ANGER" reactions.
    * :attr:`REACTION-LIKE` : The cumulative sum of "LIKE" reactions.

    Args:
        template (str): The template containing keywords.
        top_stats (dict): The top statistics, generated with ``get_top_stats()`` function.

    Returns:
        str
        
    Example:
        >>> template = "The best post is: <<TOP1-BEST-POST-REACTION>>, the second best comment is: <<TOP2-BEST-COMMENT-REACTION>>"
        >>> stats = get_top_stats(posts)
        >>> apply_stats_template(template, stats)
            'The best post is: Léa Ricot, the second best comment is: Jean Neymar'
    """
    for stat_category in top_stats.keys():
        for i in range(0, 3):
            try:
                stat = top_stats[stat_category][i]["user"]
            except:
                stat  = "None"
            template = template.replace(f"<<TOP{i+1}-{stat_category}>>", stat)
    return template



def apply_template(template, top_stats):
    template = apply_stats_template(template, top_stats)
    template = template.replace(f"<<DATE-NOW>>", datetime.now().isoformat())
    return apply_fonts_template(template)

