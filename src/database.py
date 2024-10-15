import sqlite3
from typing import Optional
from logging import getLogger

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base

from config import Member, setup_logging

setup_logging()

DATABASE = "./data/data.db"


class IdmNumber:
    """
    このclassはIDmとMMaidの対応を取得するためのclassです
    """

    Base = declarative_base()

    class IdmToMmaid(Base):
        __tablename__ = "idm_to_mmaid"
        idm = Column(String, primary_key=True)
        mmaid = Column(String)

    @staticmethod
    def get_id(idm: str) -> Optional[str]:
        """
        引数に指定されたIDmに対応するMMaidを取得します
        引数: idm - IDm
        返り値: MMaid
        """
        engine = create_engine(f"sqlite:///{DATABASE}")
        Session = sessionmaker(bind=engine)
        with Session() as session:
            entry = session.query(IdmNumber.IdmToMmaid).filter_by(idm=idm).first()
            return str(entry.mmaid) if entry else None


class MemberInfo:
    """
    このclassは入部届から class MemberInfo に関する情報を取得するためのclassです
    """

    @staticmethod
    def get_id(number: str) -> Optional[str]:
        """
        引数に指定された番号に対応するMMaidを取得します
        引数: number - 番号
        返り値: MMaid
        """
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT mmaid FROM number_to_mmaid WHERE number = ?", (number,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    @staticmethod
    def get_called_by(mmaid: str) -> Optional[str]:
        """
        引数に指定されたmmaidに対応するcalled_byを取得します
        引数: mmaid - MMaid
        返り値: called_by
        """
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT called_by FROM users WHERE mmaid = ?", (mmaid,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None


class GetMember:
    """
    このclassは番号からメンバー情報を取得するためのclassです
    """

    @staticmethod
    def get_mmaid_from_number(number: str) -> Optional[str]:
        """
        引数に指定された番号に対応するMMaidを取得します
        引数: number - 番号
        返り値: MMaid
        """
        if len(number) == 7:
            mmaid = MemberInfo.get_id(number)
            return mmaid
        elif len(number) == 16:
            mmaid = IdmNumber.get_id(number)
            return mmaid
        else:
            return None

    @staticmethod
    def get_member_from_mmaid(mmaid: str) -> Optional[Member]:
        """
        引数に指定されたmmaidに対応するメンバー情報を取得します
        引数: mmaid - MMaid
        返り値: メンバー情報 class Member (mmaid, called_by, avatar_url)
        """
        mmaid = str(mmaid)
        called_by = MemberInfo.get_called_by(mmaid) or ""
        member: Member = {
            "mmaid": mmaid,
            "called_by": called_by,
            "avatar_url": "",
        }
        return member

    @staticmethod
    def get_member(number: str) -> Optional[Member]:
        """
        引数に指定された番号に対応するメンバー情報を取得します
        引数: number - 番号
        返り値: メンバー情報 class Member (mmaid, called_by, avatar_url)
        """
        if len(number) == 7:
            mmaid = MemberInfo.get_id(number)
        elif len(number) == 16:
            mmaid = IdmNumber.get_id(number)
        else:
            return None
        member = GetMember.get_member_from_mmaid(mmaid)
        return member


if __name__ == "__main__":
    mmaid = IdmNumber.get_id("013905fca7b7e6f5")
    print(mmaid)
    mmaid = MemberInfo.get_id("2210177")
    print(mmaid)
    member = GetMember.get_member("2210177")
    print(member)
