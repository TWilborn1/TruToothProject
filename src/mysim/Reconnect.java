package mysim;

public class Reconnect {
    private int fails = 0;

    public long nextDelayMs() {
        int[] steps = {1000, 3000, 5000};
        return fails < steps.length ? steps[fails] : 10000L;
    }

    public void onFailure() { fails++; }
    public void onSuccess() { fails = 0; }
}
