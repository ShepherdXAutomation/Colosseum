public class Set<T> : IAccumulator<T>
{
    public T Accumulate(T left, T right)
    {
        return right;
    }
}
