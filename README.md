# 스치면열리는 Demo
> 같은 위치에 있는 사람들 모두 1:1 채팅이 자동으로 생성
#
### 완료된 구현
> WebSocket 이용하여 새롭게 생성되는 채팅방 및 채팅 업데이트

1. Client에서 15초 간격으로 서버로 현위치 좌표 송신
2. 서버는 해당 좌표를 일정 범위로 변환
```
(127.54432112, 54.12343221) -> (127.54432, 54.12343)
```
3. 변환된 좌표를 기준으로 같은 좌표에 있는 사람들을 확인
   1. 서버에서 유저 위치 정보를 저장하는 Dictionary `users_location`가 존재
   ```
   {(127.54432, 54.12343): [user1, user2], (127.54432, 54.12343): [user1, user3, user4]} 
   ```
   2. WebSocket로 유저 좌표가 들어올 때마다 추가 
   3. 서버는 40초 간격으로 `users_location`을 순회하며 동일한 좌표(Key)에 유저(Value)가 2명 이상 있는지 확인
   4. 100초마다 `users_location` 초기 값 {}으로 리셋 (현위치만 확인)
4. 2명 이상 있다면 2명씩 매핑하고 유저이름으로 정렬하여 채팅방 이름 생성 `user1_user2`
5. 채팅방 이름 `user1_user2`가 이미 생성되어 있는 채팅방인지 확인, 없다면 생성하고 WebSocket으로 해당되는 사용자에게 업데이트
6. `user1_user2` 채팅방을 통해 user1과 user2는 채팅
##
* **채팅방과 채팅**은 DB `ChatRoom`과 `Message` 영구 저장
* 실시간 **채팅방과 채팅** 업데이트는 WebSocket + 메모리 DB Redis 활용
* 하나의 `users_location`을 전체 Client가 공유하고 Client마다 정기 작업이 실행되지 않도록, `asgi.py`에서 서버 단일 루프로 실행하고 정기 작업
```
# 주기적 작업 시작
loop = asyncio.get_event_loop()
loop.create_task(reset_locations_periodically())
loop.create_task(check_overlap_periodically())
```

#
### 실행
1. 프로젝트 폴더로 이동 후 가상화
```
source venv/bin/activate
```
2. Docker Redis 실행
```
docker run --name redis -p 6379:6379 -d redis
```
3. WebSocket 서버까지 실행시키기 위해 uvicorn asgi으로 실행
```
uvicorn test018.asgi:application --reload
```