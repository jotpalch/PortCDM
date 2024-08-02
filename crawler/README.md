# Crawler

### Workflow of the crawler:

Step1: Extract the voyage id of all the ships listed on the [page](https://sdci.kh.twport.com.tw/khbweb/UA1007.aspx)

Step2: Use the extracted voyage id to get the newest event which can be queried on the [page](https://sdci.kh.twport.com.tw/khbweb/ShipinP.aspx?Menu=2)

### Run the demo with Docker

```bash
docker build --platform linux/amd64 -t crawler .
docker run --platform linux/amd64 --rm -v ./output:/app/output crawler:latest
```
