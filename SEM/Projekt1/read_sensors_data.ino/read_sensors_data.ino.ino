
#include <DHT11.h>
#include <SMT172.h>
#include <thermistor.h>


DHT11 dht11(3);
const int lm35_pin = A0;

thermistor therm2(A1,0);  


void setup()
{
    Serial.begin(9600);
    pinMode(8, INPUT);
    SMT172::startTemperature();
}

void loop()
{

    SMT172::startTemperature();
    /** DHT CODE**/
    dht11.readTemperature();
    dht11.readHumidity();
    double temperature1 = dht11.readTemperature();
    int humidity = dht11.readHumidity();

    /** SMT172 CODE **/
    SMT172::getTemperature();
    double temperature2 = SMT172::getTemperature();

    
    /** LM35 CODE **/   
    analogRead(lm35_pin);	     
    int tmp = analogRead(lm35_pin);	/* Read temperature1 */
    
    double temperature3 = (tmp * 4.88);	/* Convert adc value to equivalent voltage */
    temperature3 = (temperature3/10);	/* LM35 gives output of 10mv/°C */

    delay(10)

    /** Termistor NTC CODE **/
    therm2.analog2temp();
    double temperature4 = therm2.analog2temp();
    
    /** SERIAL PRINT **/    
    if (temperature1 != DHT11::ERROR_CHECKSUM && temperature1 != DHT11::ERROR_TIMEOUT &&
    humidity != DHT11::ERROR_CHECKSUM && humidity != DHT11::ERROR_TIMEOUT)
    {
        Serial.print(temperature1);
        Serial.print(" ");
        Serial.print(humidity);
        Serial.print(" ");
        Serial.print(temperature2);
        Serial.print(" ");
        Serial.print(temperature3);
        Serial.print(" ");
        Serial.println(temperature4);
    }
    else
    {
      Serial.println("Fail");
    }

    
    delay(2000);
        
}
