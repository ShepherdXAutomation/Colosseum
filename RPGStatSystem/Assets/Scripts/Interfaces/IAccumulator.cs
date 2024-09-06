public interface IAccumulator<T>
{
    T Accumulate(T left, T right);
}
