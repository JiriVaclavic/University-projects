#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "driver/gpio.h"

#include "dht11.h"
#include "esp_sntp.h"

#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "nvs_flash.h"


#define EXAMPLE_ESP_WIFI_SSID      "Nazev_wifi"
#define EXAMPLE_ESP_WIFI_PASS      "Heslo"
#define EXAMPLE_ESP_MAXIMUM_RETRY  5
static EventGroupHandle_t s_wifi_event_group;
#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT      BIT1
static int s_retry_num = 0;

/*  This function handles events related to WiFi and IP connectivity. 
    It determines what to do when the ESP32 connects or 
    disconnects from a WiFi network or obtains an IP address.
*/
static void event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_num < EXAMPLE_ESP_MAXIMUM_RETRY) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGI("readSensor_task", "retry to connect to the AP");
        } else {
            xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
        }
        ESP_LOGI("readSensor_task","connect to the AP fail");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI("readSensor_task", "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}
/*  This function is called when the SNTP client finishes synchronizing the time with the NTP server.
    It prints the time in seconds since January 1, 1970.
*/
void time_sync_cb(struct timeval *tv) {
    printf("Time sync finished: %lld\n", tv->tv_sec);
}
/*
    This function sets up the SNTP client to synchronize the time with an NTP server.
*/
void obtain_time(void)
{
    printf("SNTP starting\n");

    setenv("TZ", "UTC-2", 1);
    tzset();
    sntp_setservername(0, "pool.ntp.org");
    sntp_set_sync_interval( 15*1000 ); 
    sntp_set_sync_mode(SNTP_SYNC_MODE_IMMED); 
    sntp_init();
}
/*
    This function initializes the ESP32 as a WiFi station, connects
    to a specified access point (AP), and waits until it is connected or has failed to connect.
    It also sets up event handlers for WiFi and IP events.
*/
void wifi_init_sta(void)
{

    s_wifi_event_group = xEventGroupCreate();


    ESP_ERROR_CHECK(esp_netif_init());


    ESP_ERROR_CHECK(esp_event_loop_create_default());


    esp_netif_create_default_wifi_sta();


    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));


    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        IP_EVENT_STA_GOT_IP,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_got_ip));

    wifi_config_t wifi_config = {
        .sta = {
            .ssid = EXAMPLE_ESP_WIFI_SSID,
            .password = EXAMPLE_ESP_WIFI_PASS,
            .threshold = {
                .authmode = WIFI_AUTH_WPA2_PSK,
            },
        },
    };


    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());


    ESP_LOGI("readSensor_task", "wifi_init_sta finished.");


    EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
            WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
            pdFALSE,
            pdFALSE,
            portMAX_DELAY);


    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI("readSensor_task", "connected to ap SSID:%s password:%s",
                 EXAMPLE_ESP_WIFI_SSID, EXAMPLE_ESP_WIFI_PASS);
    } else if (bits & WIFI_FAIL_BIT) {
        ESP_LOGI("readSensor_task", "Failed to connect to SSID:%s, password:%s",
                 EXAMPLE_ESP_WIFI_SSID, EXAMPLE_ESP_WIFI_PASS);
    } else {
        ESP_LOGE("readSensor_task", "UNEXPECTED EVENT");
    }


    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, instance_got_ip));
    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(WIFI_EVENT, ESP_EVENT_ANY_ID, instance_any_id));


    vEventGroupDelete(s_wifi_event_group);
}



/*
    This function reads data from a DHT11 temperature and humidity sensor,
    and prints the results to the console along with the current time.
    It also includes a delay before the readings are taken to allow the sensor to stabilize.
*/
void readSensor_task(void *pvParameter)
{
    vTaskDelay(2000.0 / portTICK_PERIOD_MS);

    DHT11_init(GPIO_NUM_4);
        
    time_t now;
    struct tm timeinfo;
    while(1) {
        int humidity = DHT11_read().humidity;        
        if( humidity >= 0 && humidity <= 100){
            time(&now);
            localtime_r(&now, &timeinfo);
            char* time_str = asctime(&timeinfo);
            time_str[strlen(time_str) - 1] = '\0';
            int temperature = DHT11_read().temperature;
            printf("%s, %d, %d\n", time_str, temperature, humidity);        
        }        
        vTaskDelay(3000 / portTICK_PERIOD_MS);
    }
    
}