# File: stats.py
# Creation: Saturday December 5th 2020
# Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin


import json
from collections import defaultdict


def get_user_stats(posts):
    """Get per user statistics.
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
        posts (list): List of posts, retrieved from the API.

    Returns:
        dict
    """
    stats = defaultdict(lambda: defaultdict(int))
    for post in posts:
        post_author = post["user"]
        stats[post_author]["POST-COUNT"] += 1
        for post_reaction in post["reactions"]:
            # People who reacted to the post
            stats[post_author]["POST-REACTION-COUNT"] += 1
            # People who reacted
            reaction_author = post_reaction["user"]
            reaction_type = post_reaction["reaction"]
            stats[reaction_author]["REACTION-COUNT"] += 1
            stats[reaction_author][f"REACTION-{reaction_type.upper()}"] += 1

        # Update best stats
        stats[post_author]["BEST-POST-REACTION"] = max(stats[post_author]["BEST-POST-REACTION"], len(post["reactions"]))

        # look for comments
        for comment in post["comments"]:
            comment_author = comment["user"]
            stats[comment_author]["COMMENT-COUNT"] += 1
            stats[comment_author]["COMMENT-REPLY-COUNT"] += 1

            for comment_reaction in comment["reactions"]:
                # People who reacted to his comment
                stats[comment_author]["COMMENT-REACTION-COUNT"] += 1
                # People who reacted
                reaction_author = comment_reaction["user"]
                reaction_type = comment_reaction["reaction"]
                stats[reaction_author]["REACTION-COUNT"] += 1
                stats[reaction_author][f"REACTION-{reaction_type.upper()}"] += 1

            # Look for replies
            for reply in comment["replies"]:
                reply_author = comment["user"]
                stats[reply_author]["REPLY-COUNT"] += 1
                stats[reply_author]["COMMENT-REPLY-COUNT"] += 1

                for reply_reaction in reply["reactions"]:
                    # People who reacted to his comment
                    stats[reply_author]["REPLY-REACTION-COUNT"] += 1
                    # People who reacted
                    reaction_author = reply_reaction["user"]
                    reaction_type = reply_reaction["reaction"]
                    stats[reaction_author]["REACTION-COUNT"] += 1
                    stats[reaction_author][f"REACTION-{reaction_type.upper()}"] += 1

                # Update best stats
                stats[reply_author]["BEST-REPLY-REACTION"] = max(stats[reply_author]["BEST-REPLY-REACTION"], len(reply["reactions"]))
            stats[comment_author]["BEST-COMMENT-REACTION"] = max(stats[comment_author]["BEST-COMMENT-REACTION"], len(comment["reactions"]))

    return json.loads(json.dumps(stats))


def get_top_stats(posts):
    """Get the sorted top statistics.
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
        posts (list): List of posts, retrieved from the API.

    Returns:
        dict
    """
    stats = get_user_stats(posts)
    top_stats = {
        "POST-COUNT": [],
        "POST-REACTION-COUNT": [],
        "BEST-POST-REACTION": [],
        "COMMENT-COUNT": [],
        "COMMENT-REACTION-COUNT": [],
        "BEST-COMMENT-REACTION": [],
        "REPLY-COUNT": [],
        "REPLY-REACTION-COUNT": [],
        "BEST-REPLY-REACTION": [],
        "COMMENT-REPLY-COUNT": [],
        "REACTION-COUNT": [],
        "REACTION-AHAH": [],
        "REACTION-LOVE": [],
        "REACTION-CARE": [],
        "REACTION-WOW": [],
        "REACTION-SAD": [],
        "REACTION-ANGER": [],
        "REACTION-LIKE": [],
    }
    for user, user_stat in stats.items():
        for key in top_stats.keys():
            try:
                top_stats[key].append({
                    "user": user,
                    "count": user_stat[key]
                })
            except Exception:
                continue
    for key, value in top_stats.items():
        top_stats[key] = sorted(value, key=lambda key: key["count"], reverse=True)
    return top_stats
