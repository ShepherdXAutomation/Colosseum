public class Divide : IAccumulator<float>
{
    public float Accumulate(float left, float right)
    {
        return left / right;
    }
}
