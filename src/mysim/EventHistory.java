package mysim;

import java.util.ArrayList;
import java.util.List;

public class EventHistory {
    private final List<EventRecord> records = new ArrayList<>();

    public void record(Device d, String status) {
        EventRecord r = new EventRecord(d, status);
        records.add(r);
        System.out.println("[History] " + r);
    }

    public void printAll() {
        System.out.println("\n=== Session Summary ===");
        for (EventRecord r : records) System.out.println(r);
    }
}
