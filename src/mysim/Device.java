package mysim;

public class Device {
    private final String name;
    private final String address;
    private boolean connected;

    public Device(String name, String address) {
        this.name = name;
        this.address = address;
        this.connected = false;
    }

    public String getName() { return name; }
    public String getAddress() { return address; }
    public boolean isConnected() { return connected; }
    public void setConnected(boolean value) { connected = value; }

    public String shortStr() { return name + " (" + address + ")"; }
}
