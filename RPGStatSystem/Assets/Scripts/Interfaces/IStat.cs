using System;
using System.Collections.Generic;

public enum ModificationType
{
    Added,
    Removed,
    Changed
}

public class StatModifiedEventArgs : EventArgs
{

    public readonly ModificationType type;
    public readonly IStatModification modification;

    public StatModifiedEventArgs(ModificationType type, IStatModification modification)
    {
        this.type = type;
        this.modification = modification;
    }
}

public class StatModifiedEventArgs<T> : StatModifiedEventArgs
{

    public readonly T oldValue;
    public readonly T newValue;

    public StatModifiedEventArgs(ModificationType type, IStatModification modification, T oldValue, T newValue) : base (type, modification)
    {
        this.oldValue = oldValue;
        this.newValue = newValue;
    }
}

public delegate void StatModifiedEventHandler(object sender, StatModifiedEventArgs e);

public interface IStat {
    string Id { get; }
    event StatModifiedEventHandler modified;
}

public interface IStat<T> : IStat
{
    T Value { get; }
    IStatModification<T> BaseMod { get; }
    IEnumerable<IStatModification<T>> Modifications { get; }
}
