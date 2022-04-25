        filter = hid.HidDeviceFilter(vendor_id = 0x2048, product_id = 0x0302)
    hid_device = filter.get_devices()
    device = hid_device[0]
    device.open()
    print(hid_device)


    target_usage = hid.get_full_usage_id(0x00, 0x3f)
    device.set_raw_data_handler(sample_handler)
    print(target_usage)


    report = device.find_output_reports()

    print(report)
    print(report[0])

    buffer = [0xFF]*64
    buffer[0] = 63

    print(buffer)

    report[0].set_raw_data(buffer)
    report[0].send()
