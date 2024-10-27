import logging

class EventHandler:
    def handle_detected_disappearance(self, person_id):
        """
        객체가 감지된 상태에서 사라졌을 때 실행되는 함수.
        """
        logging.info(f"감지된 객체가 사라졌습니다. ID: {person_id}")
        # 감지 상태 사라짐에 대한 추가 작업

    def handle_unauthorized_disappearance(self, person_id):
        """
        비인가 상태에서 객체가 사라졌을 때 실행되는 함수.
        """
        logging.info(f"비인가 객체가 사라졌습니다. ID: {person_id}")
        # 비인가 상태 사라짐에 대한 추가 작업

    def handle_authorized_disappearance(self, person_id):
        """
        인가 상태에서 객체가 사라졌을 때 실행되는 함수.
        """
        logging.info(f"인가된 객체가 사라졌습니다. ID: {person_id}")
        # 인가 상태 사라짐에 대한 추가 작업

    def handle_unknown_disappearance(self, person_id):
        """
        알 수 없는 상태에서 객체가 사라졌을 때 실행되는 함수.
        """
        logging.info(f"알 수 없는 상태의 객체가 사라졌습니다. ID: {person_id}")
        # 알 수 없는 상태 사라짐에 대한 추가 작업
