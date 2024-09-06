public class MultiplyFloat : IAccumulator<float>
{
    public float Accumulate(float left, float right)
    {
        return left * right;
    }
}

public class MultiplyInt : IAccumulator<int>
{
    public int Accumulate(int left, int right)
    {
        return left * right;
    }
}
