package mysim;

import java.time.LocalDateTime;

public class EventRecord {
    private final LocalDateTime time;
    private final Device device;
    private final String status;

    public EventRecord(Device device, String status) {
        this.time = LocalDateTime.now();
        this.device = device;
        this.status = status;
    }

    @Override
    public String toString() {
        return time + " | " + device.shortStr() + " | " + status;
    }
}
