import uuid
from EthanChat.server.db.models.message_model import MessageModel
from EthanChat.server.db.session import with_session
from typing import Dict

@with_session
def add_message_to_db(
    session,
    conversation_id: str,
    chat_type,
    query,
    response = "",
    message_id = None,
    meta_data: Dict = {},
):
    """
    新增聊天记录
    """
    if not message_id:
        message_id = uuid.uuid4().hex
    m = MessageModel(
        id = message_id,
        conversation_id = conversation_id,
        chat_type = chat_type,
        query = query,
        response = response,
        meta_data = meta_data,
    )    
    session.add(m)
    return m.id


@with_session
def update_message_to_db(session,message_id, response: str= None, metadata:Dict =None):
    """更新已有聊天记录"""
    m = get_message_by_id(message_id)
    if m is not None:
        if response is not None:
            m.response = response
        if isinstance(metadata, dict):
            m.meta_data = metadata
        session.add(m)

        return m.id



@with_session
def get_message_by_id(session, message_id: str) -> MessageModel:
    """获取某个id对应的conversation"""
    m = session.query(MessageModel).filter_by(id = message_id).first()
    return m



@with_session
def filter_message(session, conversation_id: str, limit: int = 10):
    """获取某个conversation的limit个对话记录"""
    messages = session.query(MessageModel).filter_by(conversation_id = conversation_id) \
    .filter(MessageModel.response != "").order_by(MessageModel.create_time.desc()) \
    .limit(limit).all()

    data = []
    for m in messages:
        data.append({"query": m.query, "response": m.response,"metadata": m.meta_data})
    return data