using System;
using System.Collections;

public class ModificationModifiedEventArgs : EventArgs { 
    public readonly ModificationType type;
    public readonly IStat sender;

    public ModificationModifiedEventArgs(ModificationType type, IStat sender)
    {
        this.type = type;
        this.sender = sender;
    }
}

public class ModificationModifiedEventArgs<T> : ModificationModifiedEventArgs
{
    public readonly T oldValue;
    public readonly T newValue;

    public ModificationModifiedEventArgs(ModificationType type, IStat sender, T oldValue, T newValue) : base(type, sender)
    {
        this.oldValue = oldValue;
        this.newValue = newValue;
    } 
}

public delegate void ModificationModifiedEventHandler(object sender, ModificationModifiedEventArgs e);

public interface IStatModification
{
    string Id { get; }
    int Priority { get; }
    event ModificationModifiedEventHandler modified;

    IStat Assignee { get; }
    void Attach(IStat stat);
    void Detach();
}

public interface IStatModification<T> : IStatModification
{
    T Value { get; set; }
    T Accumulate(T currentValue);
}
