#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "nvs_flash.h"


#include "driver/gpio.h"

void readSensor_task(void *pvParameter);
void wifi_init_sta(void);
void obtain_time(void);

void app_main(void) {
    
    ESP_ERROR_CHECK(nvs_flash_init());
    wifi_init_sta();
    obtain_time();
    xTaskCreate(&readSensor_task, "readSensor_task", configMINIMAL_STACK_SIZE * 4, NULL, 5, NULL);
}