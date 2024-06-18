#include <Adafruit_PN532.h>

#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>

#include <Wire.h>
#include <SPI.h>
// библиотека для работы с RFID/NFC
#include <Adafruit_PN532.h>

// пин прерывания
#define PN532_IRQ 2
// создаём объект для работы со сканером и передаём ему два параметра
// первый — номер пина прерывания
// вторым — число 100
// от Adafruit был программный сброс шилда
// в cканере RFID/NFC 13,56 МГц (Troyka-модуль) этот пин не используется
// поэтому передаём цифру, большая чем любой пин Arduino
Adafruit_PN532 nfc(PN532_IRQ, 100);

void setup() {
  
  Serial.begin(9600);
  pinMode(9, INPUT); // объявляем пин для кнопки
  // инициализация RFID/NFC сканера
  nfc.begin();
  delay(500);
  int versiondata = nfc.getFirmwareVersion();
  // Serial.print(versiondata); печатаем номер прошивки
  if (!versiondata) {
   Serial.print("Didn't find RFID/NFC reader");
    while (1) {
     }
   }

  // Serial.println("Found RFID/NFC reader");
  // // настраиваем модуль
  nfc.SAMConfig();
  // Serial.println("Waiting for a card ...");
}

void loop() {
  uint8_t success;
  // буфер для хранения ID карты
  uint8_t uid[8];
  // размер буфера карты
 // if (Serial.available() > 0) {// проверяем готов ли принимающий компьютер читать данные (для готовности следует послать 1)
 // Serial.print("1"); // посылаем единицу
  uint8_t uidLength;
  // смотрим нажата ли кнопка, если нажата сканируем
 // Serial.print(digitalRead(9)); // до нажатия
 // Serial.println("");
 // Serial.print(digitalRead(9)); // после нажатия
 // Serial.println("");
  if(digitalRead(9)==HIGH){//если кнопка нажата ...HIGH
 
  // слушаем новые метки
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
    // если найдена карта

  if (success) {
    // выводим в консоль полученные данные
 //  Serial.println("Found a card");
   
   // Serial.print(uidLength, DEC);
    //Serial.println(" bytes");
   // Serial.print("ID Value: ");
    // nfc.PrintHex(uid, uidLength); //(uid, uidLength);
    nfc.PrintHexChar (uid, uidLength); //  печатаем номер карты
   // nfc.PrintHexChar(uid,uidLength); //печатаем номер карты
    Serial.println("");
    delay(1000);
   }
    }
    else // если не нажата
{
  Serial.println("0");
  delay(1000);
}
  }
//}