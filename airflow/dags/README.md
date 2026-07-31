macOS에서 Airflow를 다시 실행하려면 먼저 MySQL을 시작한 뒤 LaunchAgent 4개를 등록·실행하세요.

```bash
brew services start mysql
```

그다음:

```bash
for service in api-server dag-processor scheduler triggerer
do
  plist="$HOME/Library/LaunchAgents/com.airflow.${service}.plist"
  label="gui/$(id -u)/com.airflow.${service}"

  if launchctl print "$label" >/dev/null 2>&1; then
    launchctl kickstart -k "$label"
  else
    launchctl bootstrap "gui/$(id -u)" "$plist"
  fi
done
```

상태 확인:

```bash
launchctl list | grep com.airflow
```

각 서비스가 실행 중인지 자세히 확인:

```bash
for service in api-server dag-processor scheduler triggerer
do
  echo "=== $service ==="
  launchctl print "gui/$(id -u)/com.airflow.${service}" 2>/dev/null \
    | grep -E 'state =|pid =|last exit code'
done
```

오류 확인:

```bash
tail -n 100 ~/airflow/*-error.log
```

웹 접속:

[http://localhost:8080](http://localhost:8080)

서비스 방식이 아니라 간단히 한 번만 실행하려면 LaunchAgent를 실행하지 않고 다음을 사용하세요.

```bash
conda activate agent
airflow standalone
```

`standalone`과 LaunchAgent 4개를 동시에 실행하면 프로세스와 8080 포트가 중복되므로 둘 중 한 방식만 사용해야 합니다.