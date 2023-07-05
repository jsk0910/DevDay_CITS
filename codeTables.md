# 응급환자 중증도 분류 기준  
db Name : cits  
Collection Name : CodeTable  
-Data Format-  
```json
{
  "firstCode" : "A",
  "secondCode" : "A",
  "thirdCode" : "A",
  "fourthCode" : "AA",
  "Code" : 1,
  "description" : "15세 이상, 물질오용/중독, 중증 호흡곤란",
  "matchCode" : "물질오용"
}
```  
firstCode : 환자 연령대  
secondCode : 증상 분류 2단계, 증상 종류(대분류)  
thirdCode : 증상분류 3단계, 증상 종류(중분류)  
fourthCode : 증상분류 4단계, 상세 증상(소분류)  
Code : 응급도  
