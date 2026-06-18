#include "Commands/UnrealMCPBlueprintNodeCommands.h"
#include "Commands/UnrealMCPCommonUtils.h"
#include "Engine/Blueprint.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Animation/AnimClassInterface.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNodeBase.h"
#include "Animation/AnimNode_StateMachine.h"
#include "Animation/AnimStateMachineTypes.h"
#include "AnimationGraphSchema.h"
#include "AnimationStateMachineGraph.h"
#include "AnimGraphNode_StateMachineBase.h"
#include "AnimGraphNode_Base.h"
#include "AnimGraphNode_ComponentToLocalSpace.h"
#include "AnimGraphNode_ControlRig.h"
#include "AnimGraphNode_LinkedInputPose.h"
#include "AnimGraphNode_LocalToComponentSpace.h"
#include "AnimGraphNode_ModifyBone.h"
#include "AnimGraphNode_ModifyCurve.h"
#include "AnimGraphNode_RigidBody.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_Trail.h"
#include "AnimStateNodeBase.h"
#include "AnimStateTransitionNode.h"
#include "ControlRig.h"
#include "ControlRigBlueprintLegacy.h"
#include "Components/SkeletalMeshComponent.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "EdGraph/EdGraphPin.h"
#include "Editor.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Actor.h"
#include "K2Node_Event.h"
#include "K2Node_CallFunction.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "K2Node_InputAction.h"
#include "K2Node_InputAxisEvent.h"
#include "K2Node_EnhancedInputAction.h"
#include "K2Node_Self.h"
#include "K2Node_IfThenElse.h"
#include "K2Node_ExecutionSequence.h"
#include "K2Node_FunctionResult.h"
#include "K2Node_DynamicCast.h"
#include "K2Node_AddDelegate.h"
#include "K2Node_AssignDelegate.h"
#include "K2Node_CallDelegate.h"
#include "K2Node_ClearDelegate.h"
#include "K2Node_CustomEvent.h"
#include "K2Node_RemoveDelegate.h"
#include "K2Node_EnumLiteral.h"
#include "K2Node_SwitchEnum.h"
#include "K2Node_SwitchInteger.h"
#include "K2Node_EditablePinBase.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_MacroInstance.h"
#include "K2Node_CallArrayFunction.h"
#include "K2Node_MakeArray.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "GameFramework/InputSettings.h"
#include "Camera/CameraActor.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetMathLibrary.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Kismet/KismetArrayLibrary.h"
#include "EdGraphSchema_K2.h"
#include "InputAction.h"
#include "Internationalization/Text.h"
#include "Misc/PackageName.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "UObject/Class.h"
#include "UObject/UnrealType.h"
#include "Rigs/RigHierarchy.h"
#include "Rigs/RigHierarchyDefines.h"

#include <initializer_list>

// Declare the log category
DEFINE_LOG_CATEGORY_STATIC(LogUnrealMCP, Log, All);

namespace
{
UClass* LoadClassForPin(const FString& ClassPathOrName);
UEnum* LoadEnumForPin(const FString& EnumPathOrName);
FString GetPinDefaultStringForType(const TSharedPtr<FJsonValue>& Value, const FEdGraphPinType& PinType);
TSharedPtr<FJsonObject> GraphToJson(const UBlueprint* Blueprint, const UEdGraph* Graph);

bool IsBlueprintNodePlaySessionActive()
{
    return GEditor && GEditor->IsPlaySessionInProgress();
}

FString GetPinDirectionName(const UEdGraphPin* Pin)
{
    return Pin && Pin->Direction == EGPD_Output ? TEXT("output") : TEXT("input");
}

FString NormalizeAssetObjectPathForLoad(const FString& AssetPath)
{
    FString NormalizedPath = FPackageName::ExportTextPathToObjectPath(AssetPath).TrimStartAndEnd();
    NormalizedPath.TrimQuotesInline();

    if ((NormalizedPath.StartsWith(TEXT("/Game/")) || NormalizedPath.StartsWith(TEXT("/Engine/"))) && !NormalizedPath.Contains(TEXT(".")))
    {
        const FString AssetName = FPackageName::GetShortName(NormalizedPath);
        NormalizedPath = FString::Printf(TEXT("%s.%s"), *NormalizedPath, *AssetName);
    }

    return NormalizedPath;
}

FString GetPinDefaultString(const TSharedPtr<FJsonValue>& Value, const UEdGraphPin* Pin)
{
    if (!Value.IsValid())
    {
        return FString();
    }

    if (Value->Type == EJson::Boolean)
    {
        return Value->AsBool() ? TEXT("true") : TEXT("false");
    }

    if (Value->Type == EJson::Number)
    {
        if (Pin && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Int)
        {
            return FString::FromInt(FMath::RoundToInt(Value->AsNumber()));
        }
        return FString::SanitizeFloat(Value->AsNumber());
    }

    if (Value->Type == EJson::String)
    {
        return Value->AsString();
    }

    if (Value->Type == EJson::Array || Value->Type == EJson::Object)
    {
        FString Serialized;
        const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Serialized);
        FJsonSerializer::Serialize(Value, TEXT(""), Writer);
        return Serialized;
    }

    return FString();
}

FString NormalizeTypeName(const FString& TypeName)
{
    FString Normalized = TypeName.ToLower();
    Normalized.TrimStartAndEndInline();
    Normalized.ReplaceInline(TEXT(" "), TEXT(""));
    Normalized.ReplaceInline(TEXT("_"), TEXT(""));
    Normalized.ReplaceInline(TEXT("-"), TEXT(""));
    return Normalized;
}

bool GetBoolParam(const TSharedPtr<FJsonObject>& Params, const FString& FieldName, bool bDefaultValue)
{
    if (!Params.IsValid() || !Params->HasField(FieldName))
    {
        return bDefaultValue;
    }
    return Params->GetBoolField(FieldName);
}

FString GetStringParam(const TSharedPtr<FJsonObject>& Params, const FString& FieldName, const FString& DefaultValue = FString())
{
    if (!Params.IsValid())
    {
        return DefaultValue;
    }

    FString Value;
    return Params->TryGetStringField(FieldName, Value) ? Value : DefaultValue;
}

FString GetEnumTypeParam(const TSharedPtr<FJsonObject>& Params, const FString& PreferredFieldName = TEXT("enum_type"))
{
    if (!Params.IsValid())
    {
        return FString();
    }

    TArray<FString> FieldNames;
    if (!PreferredFieldName.IsEmpty())
    {
        FieldNames.Add(PreferredFieldName);
    }
    FieldNames.Add(TEXT("enum_type"));
    FieldNames.Add(TEXT("type_object"));
    FieldNames.Add(TEXT("enum_path"));

    TSet<FString> SeenFields;
    for (const FString& FieldName : FieldNames)
    {
        if (FieldName.IsEmpty() || SeenFields.Contains(FieldName))
        {
            continue;
        }
        SeenFields.Add(FieldName);

        FString Value;
        if (Params->TryGetStringField(FieldName, Value))
        {
            Value.TrimStartAndEndInline();
            if (!Value.IsEmpty())
            {
                return Value;
            }
        }
    }

    return FString();
}

const UEnum* GetEnumForPinType(const FEdGraphPinType& PinType)
{
    if (PinType.PinCategory != UEdGraphSchema_K2::PC_Byte || PinType.IsArray())
    {
        return nullptr;
    }

    return Cast<UEnum>(PinType.PinSubCategoryObject.Get());
}

bool IsEnumIndexHiddenOrSpacer(const UEnum* Enum, int32 Index)
{
    return !Enum ||
        !Enum->IsValidEnumValue(Enum->GetValueByIndex(Index)) ||
        Enum->HasMetaData(TEXT("Hidden"), Index) ||
        Enum->HasMetaData(TEXT("Spacer"), Index);
}

int32 FindFirstVisibleEnumIndex(const UEnum* Enum)
{
    if (!Enum)
    {
        return INDEX_NONE;
    }

    for (int32 Index = 0; Index < Enum->NumEnums(); ++Index)
    {
        if (!IsEnumIndexHiddenOrSpacer(Enum, Index))
        {
            return Index;
        }
    }

    return INDEX_NONE;
}

TArray<TSharedPtr<FJsonValue>> EnumEntriesToJson(const UEnum* Enum, bool bSwitchCasesOnly = false)
{
    TArray<TSharedPtr<FJsonValue>> Entries;
    if (!Enum)
    {
        return Entries;
    }

    const int32 EntryCount = bSwitchCasesOnly ? FMath::Max(0, Enum->NumEnums() - 1) : Enum->NumEnums();
    for (int32 Index = 0; Index < EntryCount; ++Index)
    {
        if (IsEnumIndexHiddenOrSpacer(Enum, Index))
        {
            continue;
        }

        TSharedPtr<FJsonObject> Entry = MakeShared<FJsonObject>();
        Entry->SetStringField(TEXT("name"), Enum->GetNameStringByIndex(Index));
        Entry->SetNumberField(TEXT("value"), static_cast<double>(Enum->GetValueByIndex(Index)));
        Entry->SetStringField(TEXT("display_name"), Enum->GetDisplayNameTextByIndex(Index).ToString());
        Entries.Add(MakeShared<FJsonValueObject>(Entry));
    }

    return Entries;
}

bool ResolveEnumValueDefaultString(const TSharedPtr<FJsonValue>& Value, const UEnum* Enum, FString& OutDefaultValue, int32& OutIndex, FString& OutError)
{
    OutDefaultValue.Reset();
    OutIndex = INDEX_NONE;
    OutError.Reset();

    if (!Enum)
    {
        OutError = TEXT("Invalid enum type");
        return false;
    }

    if (!Value.IsValid())
    {
        OutIndex = FindFirstVisibleEnumIndex(Enum);
        if (OutIndex == INDEX_NONE)
        {
            OutError = FString::Printf(TEXT("Enum has no visible values: %s"), *Enum->GetPathName());
            return false;
        }
    }
    else if (Value->Type == EJson::String)
    {
        FString RequestedValue = Value->AsString();
        RequestedValue.TrimStartAndEndInline();
        RequestedValue.TrimQuotesInline();
        if (RequestedValue.IsEmpty())
        {
            OutError = TEXT("Enum value cannot be empty");
            return false;
        }

        OutIndex = Enum->GetIndexByNameString(RequestedValue);
        if (OutIndex == INDEX_NONE && !RequestedValue.Contains(TEXT("::")))
        {
            OutIndex = Enum->GetIndexByNameString(FString::Printf(TEXT("%s::%s"), *Enum->GetName(), *RequestedValue));
        }
        if (OutIndex == INDEX_NONE)
        {
            OutIndex = Enum->GetIndexByNameString(Enum->GenerateFullEnumName(*RequestedValue));
        }
    }
    else if (Value->Type == EJson::Number)
    {
        const double NumberValue = Value->AsNumber();
        const int64 IntegerValue = static_cast<int64>(NumberValue);
        if (!FMath::IsNearlyEqual(NumberValue, static_cast<double>(IntegerValue)))
        {
            OutError = TEXT("Enum numeric default must be an integer value");
            return false;
        }

        OutIndex = Enum->GetIndexByValue(IntegerValue);
    }
    else
    {
        OutError = TEXT("Enum default must be a string enum entry or integer enum value");
        return false;
    }

    if (OutIndex == INDEX_NONE)
    {
        OutError = FString::Printf(TEXT("Enum value not found for %s"), *Enum->GetPathName());
        return false;
    }
    if (IsEnumIndexHiddenOrSpacer(Enum, OutIndex))
    {
        OutError = FString::Printf(TEXT("Enum value is hidden or spacer: %s"), *Enum->GetNameStringByIndex(OutIndex));
        return false;
    }

    OutDefaultValue = Enum->GetNameStringByIndex(OutIndex);
    return true;
}

bool GetPinDefaultStringForTypeChecked(const TSharedPtr<FJsonValue>& Value, const FEdGraphPinType& PinType, FString& OutDefaultValue, FString& OutError)
{
    OutDefaultValue.Reset();
    OutError.Reset();

    if (PinType.PinCategory == UEdGraphSchema_K2::PC_Byte && Cast<UEnum>(PinType.PinSubCategoryObject.Get()) && PinType.IsArray())
    {
        OutError = TEXT("Default values for enum arrays are not supported");
        return false;
    }
    if (PinType.PinCategory == UEdGraphSchema_K2::PC_Boolean && Value.IsValid() && Value->Type != EJson::Boolean)
    {
        OutError = TEXT("Boolean default values must be JSON booleans");
        return false;
    }

    if (const UEnum* Enum = GetEnumForPinType(PinType))
    {
        int32 EnumIndex = INDEX_NONE;
        return ResolveEnumValueDefaultString(Value, Enum, OutDefaultValue, EnumIndex, OutError);
    }

    OutDefaultValue = GetPinDefaultStringForType(Value, PinType);
    return true;
}

FString GetPinDefaultStringForType(const TSharedPtr<FJsonValue>& Value, const FEdGraphPinType& PinType)
{
    if (!Value.IsValid())
    {
        return FString();
    }

    const bool bIsVector = PinType.PinCategory == UEdGraphSchema_K2::PC_Struct && PinType.PinSubCategoryObject == TBaseStructure<FVector>::Get();
    const bool bIsRotator = PinType.PinCategory == UEdGraphSchema_K2::PC_Struct && PinType.PinSubCategoryObject == TBaseStructure<FRotator>::Get();
    const bool bIsTransform = PinType.PinCategory == UEdGraphSchema_K2::PC_Struct && PinType.PinSubCategoryObject == TBaseStructure<FTransform>::Get();

    if ((bIsVector || bIsRotator) && Value->Type == EJson::Array)
    {
        const TArray<TSharedPtr<FJsonValue>>& Values = Value->AsArray();
        const double X = Values.IsValidIndex(0) ? Values[0]->AsNumber() : 0.0;
        const double Y = Values.IsValidIndex(1) ? Values[1]->AsNumber() : 0.0;
        const double Z = Values.IsValidIndex(2) ? Values[2]->AsNumber() : 0.0;
        if (bIsRotator)
        {
            return FString::Printf(TEXT("(Pitch=%s,Yaw=%s,Roll=%s)"), *FString::SanitizeFloat(X), *FString::SanitizeFloat(Y), *FString::SanitizeFloat(Z));
        }
        return FString::Printf(TEXT("(X=%s,Y=%s,Z=%s)"), *FString::SanitizeFloat(X), *FString::SanitizeFloat(Y), *FString::SanitizeFloat(Z));
    }

    if ((bIsVector || bIsRotator || bIsTransform) && Value->Type == EJson::Object)
    {
        const TSharedPtr<FJsonObject> ObjectValue = Value->AsObject();
        if (ObjectValue.IsValid())
        {
            if (bIsTransform)
            {
                const FEdGraphPinType VectorType(UEdGraphSchema_K2::PC_Struct, NAME_None, TBaseStructure<FVector>::Get(), EPinContainerType::None, false, FEdGraphTerminalType());
                const FEdGraphPinType RotatorType(UEdGraphSchema_K2::PC_Struct, NAME_None, TBaseStructure<FRotator>::Get(), EPinContainerType::None, false, FEdGraphTerminalType());

                const TSharedPtr<FJsonValue> LocationValue = ObjectValue->TryGetField(TEXT("location")).IsValid()
                    ? ObjectValue->TryGetField(TEXT("location"))
                    : ObjectValue->TryGetField(TEXT("translation"));
                const TSharedPtr<FJsonValue> RotationValue = ObjectValue->TryGetField(TEXT("rotation"));
                const TSharedPtr<FJsonValue> ScaleValue = ObjectValue->TryGetField(TEXT("scale")).IsValid()
                    ? ObjectValue->TryGetField(TEXT("scale"))
                    : ObjectValue->TryGetField(TEXT("scale3d"));

                const FString Location = LocationValue.IsValid()
                    ? GetPinDefaultStringForType(LocationValue, VectorType)
                    : TEXT("(X=0,Y=0,Z=0)");
                const FString Rotation = RotationValue.IsValid()
                    ? GetPinDefaultStringForType(RotationValue, RotatorType)
                    : TEXT("(Pitch=0,Yaw=0,Roll=0)");
                const FString Scale = ScaleValue.IsValid()
                    ? GetPinDefaultStringForType(ScaleValue, VectorType)
                    : TEXT("(X=1,Y=1,Z=1)");
                return FString::Printf(TEXT("(Rotation=%s,Translation=%s,Scale3D=%s)"), *Rotation, *Location, *Scale);
            }

            double X = 0.0;
            double Y = 0.0;
            double Z = 0.0;
            ObjectValue->TryGetNumberField(bIsRotator ? TEXT("pitch") : TEXT("x"), X);
            ObjectValue->TryGetNumberField(bIsRotator ? TEXT("yaw") : TEXT("y"), Y);
            ObjectValue->TryGetNumberField(bIsRotator ? TEXT("roll") : TEXT("z"), Z);
            if (bIsRotator)
            {
                return FString::Printf(TEXT("(Pitch=%s,Yaw=%s,Roll=%s)"), *FString::SanitizeFloat(X), *FString::SanitizeFloat(Y), *FString::SanitizeFloat(Z));
            }
            return FString::Printf(TEXT("(X=%s,Y=%s,Z=%s)"), *FString::SanitizeFloat(X), *FString::SanitizeFloat(Y), *FString::SanitizeFloat(Z));
        }
    }

    if (Value->Type == EJson::String)
    {
        return Value->AsString();
    }
    if (Value->Type == EJson::Boolean)
    {
        return Value->AsBool() ? TEXT("true") : TEXT("false");
    }
    if (Value->Type == EJson::Number)
    {
        if (PinType.PinCategory == UEdGraphSchema_K2::PC_Int ||
            PinType.PinCategory == UEdGraphSchema_K2::PC_Int64 ||
            PinType.PinCategory == UEdGraphSchema_K2::PC_Byte)
        {
            return FString::Printf(TEXT("%lld"), static_cast<int64>(Value->AsNumber()));
        }
        return FString::SanitizeFloat(Value->AsNumber());
    }

    return GetPinDefaultString(Value, nullptr);
}

bool BuildPinTypeFromDescriptor(const FString& TypeName, const TSharedPtr<FJsonObject>& Params, const FString& ObjectFieldName, FEdGraphPinType& OutPinType, FString& OutError)
{
    const FString NormalizedType = NormalizeTypeName(TypeName);
    OutPinType = FEdGraphPinType();

    if (NormalizedType == TEXT("bool") || NormalizedType == TEXT("boolean"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Boolean;
    }
    else if (NormalizedType == TEXT("int") || NormalizedType == TEXT("integer"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Int;
    }
    else if (NormalizedType == TEXT("int64") || NormalizedType == TEXT("integer64"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Int64;
    }
    else if (NormalizedType == TEXT("float") || NormalizedType == TEXT("single"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Real;
        OutPinType.PinSubCategory = UEdGraphSchema_K2::PC_Float;
    }
    else if (NormalizedType == TEXT("double") || NormalizedType == TEXT("real"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Real;
        OutPinType.PinSubCategory = UEdGraphSchema_K2::PC_Double;
    }
    else if (NormalizedType == TEXT("string"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_String;
    }
    else if (NormalizedType == TEXT("name"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Name;
    }
    else if (NormalizedType == TEXT("text"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Text;
    }
    else if (NormalizedType == TEXT("vector"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Struct;
        OutPinType.PinSubCategoryObject = TBaseStructure<FVector>::Get();
    }
    else if (NormalizedType == TEXT("rotator"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Struct;
        OutPinType.PinSubCategoryObject = TBaseStructure<FRotator>::Get();
    }
    else if (NormalizedType == TEXT("transform"))
    {
        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Struct;
        OutPinType.PinSubCategoryObject = TBaseStructure<FTransform>::Get();
    }
    else if (NormalizedType == TEXT("enum") || NormalizedType == TEXT("byteenum"))
    {
        const FString EnumType = GetEnumTypeParam(Params, ObjectFieldName);
        if (EnumType.IsEmpty())
        {
            OutError = TEXT("Missing enum type parameter. Use 'type_object', 'enum_type', or 'enum_path'");
            return false;
        }

        UEnum* Enum = LoadEnumForPin(EnumType);
        if (!Enum)
        {
            OutError = FString::Printf(TEXT("Enum not found for %s type: %s"), *TypeName, *EnumType);
            return false;
        }

        OutPinType.PinCategory = UEdGraphSchema_K2::PC_Byte;
        OutPinType.PinSubCategoryObject = Enum;
    }
    else if (NormalizedType == TEXT("object") || NormalizedType == TEXT("class"))
    {
        const FString ClassName = GetStringParam(Params, ObjectFieldName, TEXT("Object"));
        UClass* Class = LoadClassForPin(ClassName);
        if (!Class)
        {
            OutError = FString::Printf(TEXT("Class not found for %s type: %s"), *TypeName, *ClassName);
            return false;
        }
        OutPinType.PinCategory = NormalizedType == TEXT("class") ? UEdGraphSchema_K2::PC_Class : UEdGraphSchema_K2::PC_Object;
        OutPinType.PinSubCategoryObject = Class;
    }
    else
    {
        OutError = FString::Printf(TEXT("Unsupported type descriptor: %s"), *TypeName);
        return false;
    }

    if (GetBoolParam(Params, TEXT("is_array"), false))
    {
        OutPinType.ContainerType = EPinContainerType::Array;
    }

    return true;
}

TSharedPtr<FJsonObject> PinTypeToJson(const FEdGraphPinType& PinType)
{
    TSharedPtr<FJsonObject> TypeObject = MakeShared<FJsonObject>();
    TypeObject->SetStringField(TEXT("category"), PinType.PinCategory.ToString());
    TypeObject->SetStringField(TEXT("subcategory"), PinType.PinSubCategory.ToString());
    TypeObject->SetBoolField(TEXT("is_array"), PinType.IsArray());
    if (PinType.PinSubCategoryObject.IsValid())
    {
        TypeObject->SetStringField(TEXT("subcategory_object"), PinType.PinSubCategoryObject->GetPathName());
    }
    return TypeObject;
}

TSharedPtr<FUserPinInfo> FindUserDefinedPinInfo(UK2Node_EditablePinBase* EditableNode, const FName& PinName, EEdGraphPinDirection PinDirection)
{
    if (!EditableNode)
    {
        return nullptr;
    }

    for (const TSharedPtr<FUserPinInfo>& PinInfo : EditableNode->UserDefinedPins)
    {
        if (PinInfo.IsValid() && PinInfo->PinName == PinName && PinInfo->DesiredPinDirection == PinDirection)
        {
            return PinInfo;
        }
    }

    return nullptr;
}

UObject* LoadObjectForPin(const FString& ObjectPath)
{
    const FString NormalizedPath = NormalizeAssetObjectPathForLoad(ObjectPath);
    if (NormalizedPath.IsEmpty())
    {
        return nullptr;
    }

    return LoadObject<UObject>(nullptr, *NormalizedPath);
}

UClass* LoadClassForPin(const FString& ClassPathOrName)
{
    const FString NormalizedPath = NormalizeAssetObjectPathForLoad(ClassPathOrName);
    if (UClass* Class = LoadObject<UClass>(nullptr, *NormalizedPath))
    {
        return Class;
    }

    if (UClass* Class = FindFirstObject<UClass>(*ClassPathOrName))
    {
        return Class;
    }

    FString EngineClassPath = FString::Printf(TEXT("/Script/Engine.%s"), *ClassPathOrName);
    return LoadObject<UClass>(nullptr, *EngineClassPath);
}

UEnum* LoadEnumForPin(const FString& EnumPathOrName)
{
    FString RequestedName = EnumPathOrName;
    RequestedName.TrimStartAndEndInline();
    RequestedName.TrimQuotesInline();
    if (RequestedName.IsEmpty())
    {
        return nullptr;
    }

    const FString NormalizedPath = NormalizeAssetObjectPathForLoad(RequestedName);
    if (UEnum* Enum = LoadObject<UEnum>(nullptr, *NormalizedPath))
    {
        return Enum;
    }

    if (UEnum* Enum = UClass::TryFindTypeSlow<UEnum>(
        *RequestedName,
        EFindFirstObjectOptions::ExactClass | EFindFirstObjectOptions::NativeFirst))
    {
        return Enum;
    }

    if (NormalizedPath != RequestedName)
    {
        if (UEnum* Enum = UClass::TryFindTypeSlow<UEnum>(
            *NormalizedPath,
            EFindFirstObjectOptions::ExactClass | EFindFirstObjectOptions::NativeFirst))
        {
            return Enum;
        }
    }

    if (!RequestedName.Contains(TEXT("/")) && !RequestedName.Contains(TEXT(".")))
    {
        const FString EngineEnumPath = FString::Printf(TEXT("/Script/Engine.%s"), *RequestedName);
        return LoadObject<UEnum>(nullptr, *EngineEnumPath);
    }

    return nullptr;
}

UFunction* ResolveFunctionByName(UClass* OwnerClass, const FString& FunctionName, FString& OutError)
{
    OutError.Reset();
    if (!OwnerClass)
    {
        OutError = TEXT("Invalid function owner class");
        return nullptr;
    }
    if (FunctionName.IsEmpty())
    {
        OutError = TEXT("Missing function name");
        return nullptr;
    }

    if (UFunction* Function = OwnerClass->FindFunctionByName(FName(*FunctionName)))
    {
        return Function;
    }

    TArray<UFunction*> CaseInsensitiveMatches;
    for (TFieldIterator<UFunction> FunctionIt(OwnerClass, EFieldIteratorFlags::IncludeSuper); FunctionIt; ++FunctionIt)
    {
        UFunction* Candidate = *FunctionIt;
        if (Candidate && Candidate->GetName().Equals(FunctionName, ESearchCase::IgnoreCase))
        {
            CaseInsensitiveMatches.Add(Candidate);
        }
    }

    if (CaseInsensitiveMatches.Num() == 1)
    {
        return CaseInsensitiveMatches[0];
    }
    if (CaseInsensitiveMatches.Num() > 1)
    {
        OutError = FString::Printf(TEXT("Ambiguous case-insensitive function match for '%s' on class %s"), *FunctionName, *OwnerClass->GetPathName());
        return nullptr;
    }

    OutError = FString::Printf(TEXT("Function not found: %s on class %s"), *FunctionName, *OwnerClass->GetPathName());
    return nullptr;
}

bool ValidateBlueprintCallableFunction(
    UFunction* Function,
    bool bAllowLatent,
    bool bAllowEditorOnly,
    bool bAllowWildcard,
    bool bAllowDeprecated,
    bool bAllowInternal,
    FString& OutError)
{
    OutError.Reset();
    if (!Function)
    {
        OutError = TEXT("Invalid function");
        return false;
    }

    if (!Function->HasAnyFunctionFlags(FUNC_BlueprintCallable | FUNC_BlueprintPure))
    {
        OutError = FString::Printf(TEXT("Function is not BlueprintCallable or BlueprintPure: %s"), *Function->GetPathName());
        return false;
    }
    if (!bAllowLatent && Function->HasMetaData(FBlueprintMetadata::MD_Latent))
    {
        OutError = FString::Printf(TEXT("Latent functions are not supported by this command unless 'allow_latent' is true: %s"), *Function->GetPathName());
        return false;
    }
    if (!bAllowEditorOnly && Function->HasAnyFunctionFlags(FUNC_EditorOnly))
    {
        OutError = FString::Printf(TEXT("Editor-only functions are not supported by this command unless 'allow_editor_only' is true: %s"), *Function->GetPathName());
        return false;
    }
    if (!bAllowDeprecated && Function->HasMetaData(FBlueprintMetadata::MD_DeprecatedFunction))
    {
        OutError = FString::Printf(TEXT("Deprecated functions are not supported by this command unless 'allow_deprecated' is true: %s"), *Function->GetPathName());
        return false;
    }
    if (!bAllowInternal &&
        (Function->HasMetaData(FBlueprintMetadata::MD_BlueprintInternalUseOnly) ||
         Function->HasMetaData(FBlueprintMetadata::MD_BlueprintInternalUseOnlyHierarchical)))
    {
        OutError = FString::Printf(TEXT("Blueprint-internal functions are not supported by this command unless 'allow_internal' is true: %s"), *Function->GetPathName());
        return false;
    }
    if (!bAllowWildcard &&
        (Function->HasMetaData(FBlueprintMetadata::MD_ArrayParam) ||
         Function->HasMetaData(FBlueprintMetadata::MD_CustomStructureParam) ||
         Function->HasMetaData(FBlueprintMetadata::MD_CustomThunk)))
    {
        OutError = FString::Printf(TEXT("Wildcard/custom thunk functions are not supported by this command unless 'allow_wildcard' is true: %s"), *Function->GetPathName());
        return false;
    }

    return true;
}

bool ApplyPinDefaultValueChecked(UEdGraphPin* Pin, const TSharedPtr<FJsonValue>& Value, const UEdGraphSchema_K2* K2Schema, FString& OutAppliedValue, FString& OutError)
{
    OutAppliedValue.Reset();
    OutError.Reset();

    if (!Pin || !Value.IsValid() || !K2Schema)
    {
        OutError = TEXT("Invalid pin default request");
        return false;
    }

    const FString PreviousDefaultValue = Pin->DefaultValue;
    UObject* PreviousDefaultObject = Pin->DefaultObject;
    const FText PreviousDefaultTextValue = Pin->DefaultTextValue;
    FString RequestedDefaultValue;
    UObject* RequestedDefaultObject = nullptr;
    bool bRequestedDefaultValue = false;
    bool bRequestedDefaultObject = false;

    if (Value->Type == EJson::String && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Class)
    {
        UClass* Class = LoadClassForPin(Value->AsString());
        if (!Class)
        {
            OutError = FString::Printf(TEXT("Class not found: %s"), *Value->AsString());
            return false;
        }
        RequestedDefaultObject = Class;
        bRequestedDefaultObject = true;
        K2Schema->TrySetDefaultObject(*Pin, Class);
        OutAppliedValue = Class->GetPathName();
    }
    else if (Value->Type == EJson::String && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Object)
    {
        UObject* Object = LoadObjectForPin(Value->AsString());
        if (!Object)
        {
            OutError = FString::Printf(TEXT("Object not found: %s"), *Value->AsString());
            return false;
        }
        RequestedDefaultObject = Object;
        bRequestedDefaultObject = true;
        K2Schema->TrySetDefaultObject(*Pin, Object);
        OutAppliedValue = Object->GetPathName();
    }
    else
    {
        FString DefaultResolveError;
        if (!GetPinDefaultStringForTypeChecked(Value, Pin->PinType, RequestedDefaultValue, DefaultResolveError))
        {
            OutError = DefaultResolveError;
            return false;
        }
        bRequestedDefaultValue = true;
        K2Schema->TrySetDefaultValue(*Pin, RequestedDefaultValue);
        OutAppliedValue = RequestedDefaultValue;
    }

    const FString DefaultError = K2Schema->IsCurrentPinDefaultValid(Pin);
    const bool bDefaultValueApplied = !bRequestedDefaultValue || K2Schema->DoesDefaultValueMatch(*Pin, RequestedDefaultValue);
    const bool bDefaultObjectApplied = !bRequestedDefaultObject || Pin->DefaultObject == RequestedDefaultObject;
    if (!DefaultError.IsEmpty() || !bDefaultValueApplied || !bDefaultObjectApplied)
    {
        Pin->DefaultValue = PreviousDefaultValue;
        Pin->DefaultObject = PreviousDefaultObject;
        Pin->DefaultTextValue = PreviousDefaultTextValue;
        OutError = DefaultError.IsEmpty()
            ? FString::Printf(TEXT("Requested default was not accepted. requested='%s', actual='%s'"), *RequestedDefaultValue, *Pin->GetDefaultAsString())
            : DefaultError;
        return false;
    }

    return true;
}

UEdGraphNode* FindNodeById(UEdGraph* Graph, const FString& NodeId)
{
    if (!Graph)
    {
        return nullptr;
    }

    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (Node && Node->NodeGuid.ToString() == NodeId)
        {
            return Node;
        }
    }

    return nullptr;
}

TSharedPtr<FJsonObject> PinToJson(UEdGraphPin* Pin)
{
    TSharedPtr<FJsonObject> PinObject = MakeShared<FJsonObject>();
    PinObject->SetStringField(TEXT("name"), Pin ? Pin->PinName.ToString() : FString());
    PinObject->SetStringField(TEXT("direction"), GetPinDirectionName(Pin));

    if (Pin)
    {
        PinObject->SetStringField(TEXT("category"), Pin->PinType.PinCategory.ToString());
        PinObject->SetStringField(TEXT("subcategory"), Pin->PinType.PinSubCategory.ToString());
        PinObject->SetBoolField(TEXT("is_array"), Pin->PinType.IsArray());
        PinObject->SetObjectField(TEXT("pin_type"), PinTypeToJson(Pin->PinType));
        PinObject->SetStringField(TEXT("default_value"), Pin->DefaultValue);

        if (Pin->PinType.PinSubCategoryObject.IsValid())
        {
            PinObject->SetStringField(TEXT("subcategory_object"), Pin->PinType.PinSubCategoryObject->GetPathName());
        }
        if (Pin->DefaultObject)
        {
            PinObject->SetStringField(TEXT("default_object"), Pin->DefaultObject->GetPathName());
        }

        TArray<TSharedPtr<FJsonValue>> LinkedPins;
        for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
        {
            if (!LinkedPin || !LinkedPin->GetOwningNode())
            {
                continue;
            }

            TSharedPtr<FJsonObject> LinkedPinObject = MakeShared<FJsonObject>();
            LinkedPinObject->SetStringField(TEXT("node_id"), LinkedPin->GetOwningNode()->NodeGuid.ToString());
            LinkedPinObject->SetStringField(TEXT("node_name"), LinkedPin->GetOwningNode()->GetName());
            LinkedPinObject->SetStringField(TEXT("pin_name"), LinkedPin->PinName.ToString());
            LinkedPins.Add(MakeShared<FJsonValueObject>(LinkedPinObject));
        }
        PinObject->SetArrayField(TEXT("linked_to"), LinkedPins);
    }

    return PinObject;
}

TSharedPtr<FJsonObject> NodeToJson(UEdGraphNode* Node, bool bIncludePins)
{
    TSharedPtr<FJsonObject> NodeObject = MakeShared<FJsonObject>();
    if (!Node)
    {
        return NodeObject;
    }

    NodeObject->SetStringField(TEXT("node_id"), Node->NodeGuid.ToString());
    NodeObject->SetStringField(TEXT("name"), Node->GetName());
    NodeObject->SetStringField(TEXT("class"), Node->GetClass()->GetName());
    NodeObject->SetStringField(TEXT("title"), Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString());
    NodeObject->SetNumberField(TEXT("x"), Node->NodePosX);
    NodeObject->SetNumberField(TEXT("y"), Node->NodePosY);

    if (bIncludePins)
    {
        TArray<TSharedPtr<FJsonValue>> Pins;
        for (UEdGraphPin* Pin : Node->Pins)
        {
            Pins.Add(MakeShared<FJsonValueObject>(PinToJson(Pin)));
        }
        NodeObject->SetArrayField(TEXT("pins"), Pins);
    }

    return NodeObject;
}

FString ExportPropertyValueToText(const FProperty* Property, const void* ValuePtr)
{
    if (!Property || !ValuePtr)
    {
        return FString();
    }

    FString ExportedValue;
    Property->ExportTextItem_Direct(ExportedValue, ValuePtr, nullptr, nullptr, PPF_None);
    return ExportedValue;
}

int64 GetIntegerPropertyValueAsInt64(const FNumericProperty* NumericProperty, const void* ValuePtr)
{
    if (!NumericProperty || !ValuePtr)
    {
        return 0;
    }

    if (CastField<FUInt64Property>(NumericProperty) ||
        CastField<FUInt32Property>(NumericProperty) ||
        CastField<FUInt16Property>(NumericProperty))
    {
        return static_cast<int64>(NumericProperty->GetUnsignedIntPropertyValue(ValuePtr));
    }

    return NumericProperty->GetSignedIntPropertyValue(ValuePtr);
}

TSharedPtr<FJsonValue> PropertyValueToJson(const FProperty* Property, const void* ValuePtr, int32 Depth, int32 MaxDepth);

TSharedPtr<FJsonObject> StructValueToJson(const UScriptStruct* Struct, const void* StructValuePtr, int32 Depth, int32 MaxDepth)
{
    TSharedPtr<FJsonObject> StructObject = MakeShared<FJsonObject>();
    if (!Struct || !StructValuePtr)
    {
        return StructObject;
    }

    StructObject->SetStringField(TEXT("_struct_type"), Struct->GetName());
    if (Depth >= MaxDepth)
    {
        return StructObject;
    }

    for (TFieldIterator<FProperty> It(Struct, EFieldIterationFlags::IncludeSuper); It; ++It)
    {
        const FProperty* Property = *It;
        if (!Property)
        {
            continue;
        }

        const void* ValuePtr = Property->ContainerPtrToValuePtr<void>(StructValuePtr);
        StructObject->SetField(Property->GetName(), PropertyValueToJson(Property, ValuePtr, Depth + 1, MaxDepth));
    }

    return StructObject;
}

TSharedPtr<FJsonValue> EnumValueToJson(const UEnum* Enum, int64 RawValue)
{
    TSharedPtr<FJsonObject> EnumObject = MakeShared<FJsonObject>();
    EnumObject->SetNumberField(TEXT("value"), static_cast<double>(RawValue));
    if (Enum)
    {
        EnumObject->SetStringField(TEXT("name"), Enum->GetNameStringByValue(RawValue));
        EnumObject->SetStringField(TEXT("enum_type"), Enum->GetName());
    }
    return MakeShared<FJsonValueObject>(EnumObject);
}

TSharedPtr<FJsonValue> PropertyValueToJson(const FProperty* Property, const void* ValuePtr, int32 Depth, int32 MaxDepth)
{
    if (!Property || !ValuePtr)
    {
        return MakeShared<FJsonValueNull>();
    }

    if (const FBoolProperty* BoolProperty = CastField<FBoolProperty>(Property))
    {
        return MakeShared<FJsonValueBoolean>(BoolProperty->GetPropertyValue(ValuePtr));
    }

    if (const FEnumProperty* EnumProperty = CastField<FEnumProperty>(Property))
    {
        return EnumValueToJson(
            EnumProperty->GetEnum(),
            GetIntegerPropertyValueAsInt64(EnumProperty->GetUnderlyingProperty(), ValuePtr));
    }

    if (const FByteProperty* ByteProperty = CastField<FByteProperty>(Property))
    {
        const uint8 ByteValue = ByteProperty->GetPropertyValue(ValuePtr);
        if (ByteProperty->Enum)
        {
            return EnumValueToJson(ByteProperty->Enum, ByteValue);
        }
        return MakeShared<FJsonValueNumber>(ByteValue);
    }

    if (const FNumericProperty* NumericProperty = CastField<FNumericProperty>(Property))
    {
        if (NumericProperty->IsFloatingPoint())
        {
            return MakeShared<FJsonValueNumber>(NumericProperty->GetFloatingPointPropertyValue(ValuePtr));
        }
        return MakeShared<FJsonValueNumber>(static_cast<double>(GetIntegerPropertyValueAsInt64(NumericProperty, ValuePtr)));
    }

    if (const FNameProperty* NameProperty = CastField<FNameProperty>(Property))
    {
        return MakeShared<FJsonValueString>(NameProperty->GetPropertyValue(ValuePtr).ToString());
    }

    if (const FStrProperty* StringProperty = CastField<FStrProperty>(Property))
    {
        return MakeShared<FJsonValueString>(StringProperty->GetPropertyValue(ValuePtr));
    }

    if (const FTextProperty* TextProperty = CastField<FTextProperty>(Property))
    {
        return MakeShared<FJsonValueString>(TextProperty->GetPropertyValue(ValuePtr).ToString());
    }

    if (const FObjectPropertyBase* ObjectProperty = CastField<FObjectPropertyBase>(Property))
    {
        if (const UObject* ObjectValue = ObjectProperty->GetObjectPropertyValue(ValuePtr))
        {
            return MakeShared<FJsonValueString>(ObjectValue->GetPathName());
        }
        return MakeShared<FJsonValueNull>();
    }

    if (const FSoftObjectProperty* SoftObjectProperty = CastField<FSoftObjectProperty>(Property))
    {
        return MakeShared<FJsonValueString>(SoftObjectProperty->GetPropertyValue(ValuePtr).ToString());
    }

    if (const FSoftClassProperty* SoftClassProperty = CastField<FSoftClassProperty>(Property))
    {
        return MakeShared<FJsonValueString>(SoftClassProperty->GetPropertyValue(ValuePtr).ToString());
    }

    if (const FStructProperty* StructProperty = CastField<FStructProperty>(Property))
    {
        if (Depth >= MaxDepth)
        {
            TSharedPtr<FJsonObject> StructSummary = MakeShared<FJsonObject>();
            StructSummary->SetStringField(TEXT("_struct_type"), StructProperty->Struct ? StructProperty->Struct->GetName() : FString());
            StructSummary->SetStringField(TEXT("_export_text"), ExportPropertyValueToText(Property, ValuePtr));
            return MakeShared<FJsonValueObject>(StructSummary);
        }
        return MakeShared<FJsonValueObject>(StructValueToJson(StructProperty->Struct, ValuePtr, Depth, MaxDepth));
    }

    if (const FArrayProperty* ArrayProperty = CastField<FArrayProperty>(Property))
    {
        TArray<TSharedPtr<FJsonValue>> ArrayValues;
        FScriptArrayHelper Helper(ArrayProperty, ValuePtr);
        for (int32 Index = 0; Index < Helper.Num(); ++Index)
        {
            ArrayValues.Add(PropertyValueToJson(ArrayProperty->Inner, Helper.GetRawPtr(Index), Depth + 1, MaxDepth));
        }
        return MakeShared<FJsonValueArray>(ArrayValues);
    }

    return MakeShared<FJsonValueString>(ExportPropertyValueToText(Property, ValuePtr));
}

TSharedPtr<FJsonObject> AnimGraphNodeSettingsToJson(UAnimGraphNode_Base* AnimGraphNode, int32 MaxDepth)
{
    TSharedPtr<FJsonObject> SettingsObject = MakeShared<FJsonObject>();
    if (!AnimGraphNode)
    {
        SettingsObject->SetBoolField(TEXT("has_anim_node_struct"), false);
        return SettingsObject;
    }

    FStructProperty* NodeProperty = AnimGraphNode->GetFNodeProperty();
    if (!NodeProperty || !NodeProperty->Struct)
    {
        SettingsObject->SetBoolField(TEXT("has_anim_node_struct"), false);
        return SettingsObject;
    }

    void* NodeValuePtr = NodeProperty->ContainerPtrToValuePtr<void>(AnimGraphNode);
    SettingsObject->SetBoolField(TEXT("has_anim_node_struct"), true);
    SettingsObject->SetStringField(TEXT("anim_node_property"), NodeProperty->GetName());
    SettingsObject->SetStringField(TEXT("anim_node_struct_type"), NodeProperty->Struct->GetName());
    SettingsObject->SetObjectField(TEXT("anim_node_properties"), StructValueToJson(NodeProperty->Struct, NodeValuePtr, 0, MaxDepth));
    return SettingsObject;
}

TSharedPtr<FJsonObject> AnimStateNodeToJson(const UBlueprint* Blueprint, UAnimStateNodeBase* StateNode, bool bIncludePins)
{
    TSharedPtr<FJsonObject> StateObject = MakeShared<FJsonObject>();
    if (!StateNode)
    {
        StateObject->SetBoolField(TEXT("valid"), false);
        return StateObject;
    }

    StateObject = NodeToJson(StateNode, bIncludePins);
    StateObject->SetBoolField(TEXT("valid"), true);
    StateObject->SetStringField(TEXT("state_name"), StateNode->GetStateName());

    if (UEdGraph* BoundGraph = StateNode->GetBoundGraph())
    {
        StateObject->SetObjectField(TEXT("bound_graph"), GraphToJson(Blueprint, BoundGraph));
    }

    return StateObject;
}

TSharedPtr<FJsonObject> AnimStateTransitionSettingsToJson(const UAnimStateTransitionNode* TransitionNode)
{
    TSharedPtr<FJsonObject> SettingsObject = MakeShared<FJsonObject>();
    if (!TransitionNode)
    {
        return SettingsObject;
    }

    SettingsObject->SetNumberField(TEXT("priority_order"), TransitionNode->PriorityOrder);
    SettingsObject->SetNumberField(TEXT("crossfade_duration"), TransitionNode->CrossfadeDuration);
    SettingsObject->SetField(TEXT("blend_mode"), EnumValueToJson(StaticEnum<EAlphaBlendOption>(), static_cast<int64>(TransitionNode->BlendMode)));
    SettingsObject->SetBoolField(TEXT("automatic_rule_based_on_sequence_player_in_state"), TransitionNode->bAutomaticRuleBasedOnSequencePlayerInState);
    SettingsObject->SetNumberField(TEXT("automatic_rule_trigger_time"), TransitionNode->AutomaticRuleTriggerTime);
    SettingsObject->SetNumberField(TEXT("min_time_before_reentry"), TransitionNode->MinTimeBeforeReentry);
    SettingsObject->SetStringField(TEXT("sync_group_name_to_require_valid_markers_rule"), TransitionNode->SyncGroupNameToRequireValidMarkersRule.ToString());
    SettingsObject->SetField(TEXT("logic_type"), EnumValueToJson(StaticEnum<ETransitionLogicType::Type>(), TransitionNode->LogicType.GetValue()));
    SettingsObject->SetBoolField(TEXT("bidirectional"), TransitionNode->Bidirectional);
    SettingsObject->SetBoolField(TEXT("disabled"), TransitionNode->bDisabled);
    SettingsObject->SetBoolField(TEXT("shared_rules"), TransitionNode->bSharedRules);
    SettingsObject->SetStringField(TEXT("shared_rules_name"), TransitionNode->SharedRulesName);
    SettingsObject->SetStringField(TEXT("shared_rules_guid"), TransitionNode->SharedRulesGuid.ToString());
    SettingsObject->SetBoolField(TEXT("shared_crossfade"), TransitionNode->bSharedCrossfade);
    SettingsObject->SetStringField(TEXT("shared_crossfade_name"), TransitionNode->SharedCrossfadeName);
    SettingsObject->SetStringField(TEXT("shared_crossfade_guid"), TransitionNode->SharedCrossfadeGuid.ToString());
    SettingsObject->SetNumberField(TEXT("shared_crossfade_index"), TransitionNode->SharedCrossfadeIdx);
    SettingsObject->SetBoolField(TEXT("allow_inertialization_for_self_transitions"), TransitionNode->bAllowInertializationForSelfTransitions);
    SettingsObject->SetStringField(TEXT("custom_blend_curve"), TransitionNode->CustomBlendCurve ? TransitionNode->CustomBlendCurve->GetPathName() : FString());
    SettingsObject->SetBoolField(TEXT("has_custom_transition_graph"), TransitionNode->GetCustomTransitionGraph() != nullptr);
    SettingsObject->SetBoolField(TEXT("is_bound_graph_shared"), TransitionNode->IsBoundGraphShared());
    return SettingsObject;
}

TSharedPtr<FJsonObject> TransitionGraphNodesToJson(const UBlueprint* Blueprint, UEdGraph* Graph, bool bIncludePins, int32 MaxNodes)
{
    TSharedPtr<FJsonObject> GraphObject = GraphToJson(Blueprint, Graph);
    if (!Graph)
    {
        return GraphObject;
    }

    TArray<TSharedPtr<FJsonValue>> Nodes;
    int32 AddedNodeCount = 0;
    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (!Node)
        {
            continue;
        }

        if (MaxNodes >= 0 && AddedNodeCount >= MaxNodes)
        {
            break;
        }

        Nodes.Add(MakeShared<FJsonValueObject>(NodeToJson(Node, bIncludePins)));
        ++AddedNodeCount;
    }

    GraphObject->SetArrayField(TEXT("nodes"), Nodes);
    GraphObject->SetNumberField(TEXT("included_node_count"), AddedNodeCount);
    GraphObject->SetBoolField(TEXT("truncated"), MaxNodes >= 0 && Graph->Nodes.Num() > MaxNodes);
    return GraphObject;
}

TArray<TSharedPtr<FJsonValue>> VectorToJsonArray(const FVector& Vector)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    Values.Add(MakeShared<FJsonValueNumber>(Vector.X));
    Values.Add(MakeShared<FJsonValueNumber>(Vector.Y));
    Values.Add(MakeShared<FJsonValueNumber>(Vector.Z));
    return Values;
}

TSharedPtr<FJsonValue> VectorToJsonValue(const FVector& Vector)
{
    return MakeShared<FJsonValueArray>(VectorToJsonArray(Vector));
}

bool TryGetNumberFromObjectField(const TSharedPtr<FJsonObject>& Object, const FString& LowerName, const FString& UpperName, double& OutValue)
{
    return Object.IsValid() && (Object->TryGetNumberField(LowerName, OutValue) || Object->TryGetNumberField(UpperName, OutValue));
}

bool JsonValueToVector(const TSharedPtr<FJsonValue>& Value, FVector& OutVector)
{
    if (!Value.IsValid())
    {
        return false;
    }

    if (Value->Type == EJson::Array)
    {
        const TArray<TSharedPtr<FJsonValue>>& Values = Value->AsArray();
        if (Values.Num() < 3)
        {
            return false;
        }
        OutVector = FVector(
            Values[0].IsValid() ? Values[0]->AsNumber() : 0.0,
            Values[1].IsValid() ? Values[1]->AsNumber() : 0.0,
            Values[2].IsValid() ? Values[2]->AsNumber() : 0.0);
        return true;
    }

    if (Value->Type == EJson::Object)
    {
        const TSharedPtr<FJsonObject> Object = Value->AsObject();
        double X = 0.0;
        double Y = 0.0;
        double Z = 0.0;
        if (!TryGetNumberFromObjectField(Object, TEXT("x"), TEXT("X"), X) ||
            !TryGetNumberFromObjectField(Object, TEXT("y"), TEXT("Y"), Y) ||
            !TryGetNumberFromObjectField(Object, TEXT("z"), TEXT("Z"), Z))
        {
            return false;
        }
        OutVector = FVector(X, Y, Z);
        return true;
    }

    return false;
}

bool JsonValueToRotator(const TSharedPtr<FJsonValue>& Value, FRotator& OutRotator)
{
    FVector Vector;
    if (JsonValueToVector(Value, Vector))
    {
        OutRotator = FRotator(Vector.X, Vector.Y, Vector.Z);
        return true;
    }
    return false;
}

bool JsonValueToTransform(const TSharedPtr<FJsonValue>& Value, FTransform& OutTransform)
{
    if (!Value.IsValid() || Value->Type != EJson::Object)
    {
        return false;
    }

    const TSharedPtr<FJsonObject> Object = Value->AsObject();
    if (!Object.IsValid())
    {
        return false;
    }

    FVector Translation = FVector::ZeroVector;
    FRotator Rotation = FRotator::ZeroRotator;
    FVector Scale = FVector::OneVector;
    bool bHasAnyField = false;

    const TSharedPtr<FJsonValue> TranslationValue = Object->TryGetField(TEXT("translation")).IsValid()
        ? Object->TryGetField(TEXT("translation"))
        : Object->TryGetField(TEXT("location"));
    if (TranslationValue.IsValid() && JsonValueToVector(TranslationValue, Translation))
    {
        bHasAnyField = true;
    }

    if (const TSharedPtr<FJsonValue> RotationValue = Object->TryGetField(TEXT("rotation")))
    {
        if (JsonValueToRotator(RotationValue, Rotation))
        {
            bHasAnyField = true;
        }
    }

    const TSharedPtr<FJsonValue> ScaleValue = Object->TryGetField(TEXT("scale")).IsValid()
        ? Object->TryGetField(TEXT("scale"))
        : Object->TryGetField(TEXT("scale3d"));
    if (ScaleValue.IsValid() && JsonValueToVector(ScaleValue, Scale))
    {
        bHasAnyField = true;
    }

    if (!bHasAnyField)
    {
        return false;
    }

    OutTransform = FTransform(Rotation, Translation, Scale);
    return true;
}

bool SetUObjectPropertyFromJson(UObject* Target, const FString& PropertyName, const TSharedPtr<FJsonValue>& Value, FString& OutError)
{
    OutError.Reset();
    if (!Target)
    {
        OutError = TEXT("Invalid target object");
        return false;
    }
    if (PropertyName.TrimStartAndEnd().IsEmpty())
    {
        OutError = TEXT("Property name cannot be empty");
        return false;
    }
    if (!Value.IsValid())
    {
        OutError = FString::Printf(TEXT("Missing value for property '%s'"), *PropertyName);
        return false;
    }

    FProperty* Property = Target->GetClass()->FindPropertyByName(FName(*PropertyName));
    if (!Property)
    {
        OutError = FString::Printf(TEXT("Property '%s' not found on %s"), *PropertyName, *Target->GetClass()->GetName());
        return false;
    }

    void* ValuePtr = Property->ContainerPtrToValuePtr<void>(Target);
    if (!ValuePtr)
    {
        OutError = FString::Printf(TEXT("Could not resolve property memory for '%s'"), *PropertyName);
        return false;
    }

    if (FBoolProperty* BoolProperty = CastField<FBoolProperty>(Property))
    {
        if (Value->Type != EJson::Boolean)
        {
            OutError = FString::Printf(TEXT("Property '%s' expects a boolean"), *PropertyName);
            return false;
        }
        BoolProperty->SetPropertyValue(ValuePtr, Value->AsBool());
        return true;
    }

    if (FNumericProperty* NumericProperty = CastField<FNumericProperty>(Property))
    {
        if (Value->Type != EJson::Number)
        {
            OutError = FString::Printf(TEXT("Property '%s' expects a number"), *PropertyName);
            return false;
        }
        if (NumericProperty->IsFloatingPoint())
        {
            NumericProperty->SetFloatingPointPropertyValue(ValuePtr, Value->AsNumber());
        }
        else if (CastField<FUInt64Property>(NumericProperty) ||
            CastField<FUInt32Property>(NumericProperty) ||
            CastField<FUInt16Property>(NumericProperty))
        {
            NumericProperty->SetIntPropertyValue(ValuePtr, static_cast<uint64>(FMath::Max(0.0, Value->AsNumber())));
        }
        else
        {
            NumericProperty->SetIntPropertyValue(ValuePtr, static_cast<int64>(Value->AsNumber()));
        }
        return true;
    }

    if (FNameProperty* NameProperty = CastField<FNameProperty>(Property))
    {
        if (Value->Type != EJson::String)
        {
            OutError = FString::Printf(TEXT("Property '%s' expects a string/name"), *PropertyName);
            return false;
        }
        NameProperty->SetPropertyValue(ValuePtr, FName(*Value->AsString()));
        return true;
    }

    if (FStrProperty* StringProperty = CastField<FStrProperty>(Property))
    {
        if (Value->Type != EJson::String)
        {
            OutError = FString::Printf(TEXT("Property '%s' expects a string"), *PropertyName);
            return false;
        }
        StringProperty->SetPropertyValue(ValuePtr, Value->AsString());
        return true;
    }

    if (FStructProperty* StructProperty = CastField<FStructProperty>(Property))
    {
        if (StructProperty->Struct == TBaseStructure<FVector>::Get())
        {
            FVector VectorValue;
            if (!JsonValueToVector(Value, VectorValue))
            {
                OutError = FString::Printf(TEXT("Property '%s' expects a vector array/object"), *PropertyName);
                return false;
            }
            *static_cast<FVector*>(ValuePtr) = VectorValue;
            return true;
        }

        if (StructProperty->Struct == TBaseStructure<FRotator>::Get())
        {
            FRotator RotatorValue;
            if (!JsonValueToRotator(Value, RotatorValue))
            {
                OutError = FString::Printf(TEXT("Property '%s' expects a rotator array/object"), *PropertyName);
                return false;
            }
            *static_cast<FRotator*>(ValuePtr) = RotatorValue;
            return true;
        }

        if (StructProperty->Struct == TBaseStructure<FTransform>::Get())
        {
            FTransform TransformValue;
            if (!JsonValueToTransform(Value, TransformValue))
            {
                OutError = FString::Printf(TEXT("Property '%s' expects a transform object"), *PropertyName);
                return false;
            }
            *static_cast<FTransform*>(ValuePtr) = TransformValue;
            return true;
        }
    }

    OutError = FString::Printf(TEXT("Unsupported property type for '%s': %s"), *PropertyName, *Property->GetClass()->GetName());
    return false;
}

TSharedPtr<FJsonValue> GetUObjectPropertyJson(UObject* Target, const FString& PropertyName)
{
    if (!Target)
    {
        return MakeShared<FJsonValueNull>();
    }

    FProperty* Property = Target->GetClass()->FindPropertyByName(FName(*PropertyName));
    if (!Property)
    {
        return MakeShared<FJsonValueNull>();
    }

    void* ValuePtr = Property->ContainerPtrToValuePtr<void>(Target);
    return PropertyValueToJson(Property, ValuePtr, 0, 3);
}

FString RigElementTypeToString(ERigElementType Type)
{
    switch (Type)
    {
    case ERigElementType::Bone:
        return TEXT("Bone");
    case ERigElementType::Null:
        return TEXT("Null");
    case ERigElementType::Control:
        return TEXT("Control");
    case ERigElementType::Curve:
        return TEXT("Curve");
    case ERigElementType::Reference:
        return TEXT("Reference");
    case ERigElementType::Connector:
        return TEXT("Connector");
    case ERigElementType::Socket:
        return TEXT("Socket");
    default:
        return TEXT("None");
    }
}

bool ParseRigElementType(const FString& RawValue, ERigElementType& OutType)
{
    const FString Value = RawValue.TrimStartAndEnd().Replace(TEXT(" "), TEXT("")).Replace(TEXT("_"), TEXT(""));
    if (Value.Equals(TEXT("Bone"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Bone;
        return true;
    }
    if (Value.Equals(TEXT("Null"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Null;
        return true;
    }
    if (Value.Equals(TEXT("Control"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Control;
        return true;
    }
    if (Value.Equals(TEXT("Curve"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Curve;
        return true;
    }
    if (Value.Equals(TEXT("Reference"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Reference;
        return true;
    }
    if (Value.Equals(TEXT("Connector"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Connector;
        return true;
    }
    if (Value.Equals(TEXT("Socket"), ESearchCase::IgnoreCase))
    {
        OutType = ERigElementType::Socket;
        return true;
    }
    return false;
}

bool ResolveRigElementKey(URigHierarchy* Hierarchy, const FString& ElementSpec, FRigElementKey& OutKey)
{
    if (!Hierarchy)
    {
        return false;
    }

    FString TypeText;
    FString NameText = ElementSpec;
    if (ElementSpec.Split(TEXT(":"), &TypeText, &NameText))
    {
        ERigElementType ParsedType = ERigElementType::None;
        if (ParseRigElementType(TypeText, ParsedType))
        {
            const FRigElementKey TypedKey(FName(*NameText), ParsedType);
            if (Hierarchy->Contains(TypedKey))
            {
                OutKey = TypedKey;
                return true;
            }
        }
    }

    static const ERigElementType ProbeTypes[] = {
        ERigElementType::Bone,
        ERigElementType::Control,
        ERigElementType::Null,
        ERigElementType::Reference,
        ERigElementType::Connector,
        ERigElementType::Socket,
        ERigElementType::Curve
    };

    for (const ERigElementType Type : ProbeTypes)
    {
        const FRigElementKey Candidate(FName(*NameText), Type);
        if (Hierarchy->Contains(Candidate))
        {
            OutKey = Candidate;
            return true;
        }
    }

    return false;
}

TSharedPtr<FJsonObject> TransformToJsonObject(const FTransform& Transform)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    Object->SetArrayField(TEXT("translation"), VectorToJsonArray(Transform.GetLocation()));

    const FQuat Rotation = Transform.GetRotation();
    TArray<TSharedPtr<FJsonValue>> QuatValues;
    QuatValues.Add(MakeShared<FJsonValueNumber>(Rotation.X));
    QuatValues.Add(MakeShared<FJsonValueNumber>(Rotation.Y));
    QuatValues.Add(MakeShared<FJsonValueNumber>(Rotation.Z));
    QuatValues.Add(MakeShared<FJsonValueNumber>(Rotation.W));
    Object->SetArrayField(TEXT("rotation"), QuatValues);

    const FRotator Rotator = Rotation.Rotator();
    TArray<TSharedPtr<FJsonValue>> RotatorValues;
    RotatorValues.Add(MakeShared<FJsonValueNumber>(Rotator.Pitch));
    RotatorValues.Add(MakeShared<FJsonValueNumber>(Rotator.Yaw));
    RotatorValues.Add(MakeShared<FJsonValueNumber>(Rotator.Roll));
    Object->SetArrayField(TEXT("rotation_euler"), RotatorValues);

    Object->SetArrayField(TEXT("scale"), VectorToJsonArray(Transform.GetScale3D()));
    return Object;
}

struct FControlRigDirectProbeCase
{
    FString Name;
    TMap<FString, TSharedPtr<FJsonValue>> PropertyValues;
    TMap<FName, double> CurveValues;
};

void AddProbeProperty(FControlRigDirectProbeCase& ProbeCase, const FString& PropertyName, const TSharedPtr<FJsonValue>& Value)
{
    if (!PropertyName.IsEmpty() && Value.IsValid())
    {
        ProbeCase.PropertyValues.Add(PropertyName, Value);
    }
}

FControlRigDirectProbeCase MakeDefaultControlRigProbeCase(
    const FString& Name,
    bool bShouldTrace,
    const FVector& InteractionLocation,
    double IKBlendL,
    double IKBlendInteract,
    const FString& ShouldTracePropertyName,
    const FString& InteractionLocationPropertyName)
{
    FControlRigDirectProbeCase ProbeCase;
    ProbeCase.Name = Name;
    AddProbeProperty(ProbeCase, ShouldTracePropertyName, MakeShared<FJsonValueBoolean>(bShouldTrace));
    AddProbeProperty(ProbeCase, InteractionLocationPropertyName, VectorToJsonValue(InteractionLocation));
    ProbeCase.CurveValues.Add(FName(TEXT("IKBlend_l")), IKBlendL);
    ProbeCase.CurveValues.Add(FName(TEXT("IK_blend_interact")), IKBlendInteract);
    return ProbeCase;
}

TArray<FControlRigDirectProbeCase> BuildDefaultControlRigProbeCases(
    const FString& ShouldTracePropertyName,
    const FString& InteractionLocationPropertyName)
{
    TArray<FControlRigDirectProbeCase> Cases;
    Cases.Add(MakeDefaultControlRigProbeCase(TEXT("baseline_false_curves0"), false, FVector::ZeroVector, 0.0, 0.0, ShouldTracePropertyName, InteractionLocationPropertyName));
    Cases.Add(MakeDefaultControlRigProbeCase(TEXT("trace_true_curves0"), true, FVector::ZeroVector, 0.0, 0.0, ShouldTracePropertyName, InteractionLocationPropertyName));
    Cases.Add(MakeDefaultControlRigProbeCase(TEXT("trace_true_ikblend_l1"), true, FVector::ZeroVector, 1.0, 0.0, ShouldTracePropertyName, InteractionLocationPropertyName));
    Cases.Add(MakeDefaultControlRigProbeCase(TEXT("trace_true_interact_curve1_zero_loc"), true, FVector::ZeroVector, 0.0, 1.0, ShouldTracePropertyName, InteractionLocationPropertyName));
    Cases.Add(MakeDefaultControlRigProbeCase(TEXT("trace_true_all_curves1_high_loc"), true, FVector(0.0, 0.0, 120.0), 1.0, 1.0, ShouldTracePropertyName, InteractionLocationPropertyName));
    Cases.Add(MakeDefaultControlRigProbeCase(TEXT("trace_true_all_curves1_side_loc"), true, FVector(80.0, -40.0, 80.0), 1.0, 1.0, ShouldTracePropertyName, InteractionLocationPropertyName));
    return Cases;
}

void AddJsonObjectFieldsAsProperties(FControlRigDirectProbeCase& ProbeCase, const TSharedPtr<FJsonObject>& Object)
{
    if (!Object.IsValid())
    {
        return;
    }

    for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : Object->Values)
    {
        AddProbeProperty(ProbeCase, Pair.Key, Pair.Value);
    }
}

TArray<FControlRigDirectProbeCase> ParseControlRigProbeCases(
    const TSharedPtr<FJsonObject>& Params,
    const FString& ShouldTracePropertyName,
    const FString& InteractionLocationPropertyName)
{
    if (!Params.IsValid())
    {
        return BuildDefaultControlRigProbeCases(ShouldTracePropertyName, InteractionLocationPropertyName);
    }

    const TArray<TSharedPtr<FJsonValue>>* CaseValues = nullptr;
    if (!Params->TryGetArrayField(TEXT("cases"), CaseValues) || !CaseValues || CaseValues->Num() == 0)
    {
        return BuildDefaultControlRigProbeCases(ShouldTracePropertyName, InteractionLocationPropertyName);
    }

    TArray<FControlRigDirectProbeCase> Cases;
    for (int32 CaseIndex = 0; CaseIndex < CaseValues->Num(); ++CaseIndex)
    {
        const TSharedPtr<FJsonValue>& CaseValue = (*CaseValues)[CaseIndex];
        if (!CaseValue.IsValid() || CaseValue->Type != EJson::Object)
        {
            continue;
        }

        const TSharedPtr<FJsonObject> CaseObject = CaseValue->AsObject();
        if (!CaseObject.IsValid())
        {
            continue;
        }

        FControlRigDirectProbeCase ProbeCase;
        ProbeCase.Name = GetStringParam(CaseObject, TEXT("name"), FString::Printf(TEXT("case_%d"), CaseIndex));

        const TSharedPtr<FJsonObject>* PropertiesObject = nullptr;
        if (CaseObject->TryGetObjectField(TEXT("properties"), PropertiesObject) && PropertiesObject)
        {
            AddJsonObjectFieldsAsProperties(ProbeCase, *PropertiesObject);
        }

        if (const TSharedPtr<FJsonValue> ShouldTraceValue = CaseObject->TryGetField(TEXT("should_trace")))
        {
            AddProbeProperty(ProbeCase, ShouldTracePropertyName, ShouldTraceValue);
        }

        TSharedPtr<FJsonValue> LocationValue = CaseObject->TryGetField(TEXT("interaction_world_location"));
        if (!LocationValue.IsValid())
        {
            LocationValue = CaseObject->TryGetField(TEXT("loc"));
        }
        if (LocationValue.IsValid())
        {
            AddProbeProperty(ProbeCase, InteractionLocationPropertyName, LocationValue);
        }

        const TSharedPtr<FJsonObject>* CurvesObject = nullptr;
        if (CaseObject->TryGetObjectField(TEXT("curves"), CurvesObject) && CurvesObject && CurvesObject->IsValid())
        {
            for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : (*CurvesObject)->Values)
            {
                if (Pair.Value.IsValid() && Pair.Value->Type == EJson::Number)
                {
                    ProbeCase.CurveValues.Add(FName(*Pair.Key), Pair.Value->AsNumber());
                }
            }
        }

        Cases.Add(ProbeCase);
    }

    return Cases.Num() > 0
        ? Cases
        : BuildDefaultControlRigProbeCases(ShouldTracePropertyName, InteractionLocationPropertyName);
}

FControlRigDirectProbeCase BuildDefaultControlRigPrePostCase(
    const FString& ShouldTracePropertyName,
    const FString& InteractionLocationPropertyName)
{
    return MakeDefaultControlRigProbeCase(
        TEXT("forced_driver_side"),
        true,
        FVector(80.0, -40.0, 80.0),
        1.0,
        1.0,
        ShouldTracePropertyName,
        InteractionLocationPropertyName);
}

TArray<FControlRigDirectProbeCase> ParseControlRigPrePostCases(
    const TSharedPtr<FJsonObject>& Params,
    const FString& ShouldTracePropertyName,
    const FString& InteractionLocationPropertyName)
{
    if (!Params.IsValid())
    {
        TArray<FControlRigDirectProbeCase> Cases;
        Cases.Add(BuildDefaultControlRigPrePostCase(ShouldTracePropertyName, InteractionLocationPropertyName));
        return Cases;
    }

    const TArray<TSharedPtr<FJsonValue>>* CaseValues = nullptr;
    if (Params->TryGetArrayField(TEXT("cases"), CaseValues) && CaseValues && CaseValues->Num() > 0)
    {
        return ParseControlRigProbeCases(Params, ShouldTracePropertyName, InteractionLocationPropertyName);
    }

    FControlRigDirectProbeCase ProbeCase;
    ProbeCase.Name = GetStringParam(Params, TEXT("name"), TEXT("forced_driver_side"));

    const TSharedPtr<FJsonObject>* PropertiesObject = nullptr;
    if (Params->TryGetObjectField(TEXT("properties"), PropertiesObject) && PropertiesObject)
    {
        AddJsonObjectFieldsAsProperties(ProbeCase, *PropertiesObject);
    }
    if (Params->TryGetObjectField(TEXT("input_defaults"), PropertiesObject) && PropertiesObject)
    {
        AddJsonObjectFieldsAsProperties(ProbeCase, *PropertiesObject);
    }

    if (const TSharedPtr<FJsonValue> ShouldTraceValue = Params->TryGetField(TEXT("should_trace")))
    {
        AddProbeProperty(ProbeCase, ShouldTracePropertyName, ShouldTraceValue);
    }
    else if (!ProbeCase.PropertyValues.Contains(ShouldTracePropertyName))
    {
        AddProbeProperty(ProbeCase, ShouldTracePropertyName, MakeShared<FJsonValueBoolean>(true));
    }

    TSharedPtr<FJsonValue> LocationValue = Params->TryGetField(TEXT("interaction_world_location"));
    if (!LocationValue.IsValid())
    {
        LocationValue = Params->TryGetField(TEXT("loc"));
    }
    if (LocationValue.IsValid())
    {
        AddProbeProperty(ProbeCase, InteractionLocationPropertyName, LocationValue);
    }
    else if (!ProbeCase.PropertyValues.Contains(InteractionLocationPropertyName))
    {
        AddProbeProperty(ProbeCase, InteractionLocationPropertyName, VectorToJsonValue(FVector(80.0, -40.0, 80.0)));
    }

    const TSharedPtr<FJsonObject>* CurvesObject = nullptr;
    if ((Params->TryGetObjectField(TEXT("curve_values"), CurvesObject) || Params->TryGetObjectField(TEXT("curves"), CurvesObject)) && CurvesObject && CurvesObject->IsValid())
    {
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : (*CurvesObject)->Values)
        {
            if (Pair.Value.IsValid() && Pair.Value->Type == EJson::Number)
            {
                ProbeCase.CurveValues.Add(FName(*Pair.Key), Pair.Value->AsNumber());
            }
        }
    }

    if (!ProbeCase.CurveValues.Contains(FName(TEXT("IKBlend_l"))))
    {
        ProbeCase.CurveValues.Add(FName(TEXT("IKBlend_l")), 1.0);
    }
    if (!ProbeCase.CurveValues.Contains(FName(TEXT("IK_blend_interact"))))
    {
        ProbeCase.CurveValues.Add(FName(TEXT("IK_blend_interact")), 1.0);
    }

    TArray<FControlRigDirectProbeCase> Cases;
    Cases.Add(ProbeCase);
    return Cases;
}

TArray<FString> GetStringArrayParam(const TSharedPtr<FJsonObject>& Params, const FString& FieldName, const TArray<FString>& Defaults)
{
    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Params.IsValid() || !Params->TryGetArrayField(FieldName, Values) || !Values || Values->Num() == 0)
    {
        return Defaults;
    }

    TArray<FString> Result;
    for (const TSharedPtr<FJsonValue>& Value : *Values)
    {
        if (!Value.IsValid())
        {
            continue;
        }
        if (Value->Type == EJson::String)
        {
            Result.Add(Value->AsString());
        }
        else if (Value->Type == EJson::Object)
        {
            const TSharedPtr<FJsonObject> Object = Value->AsObject();
            if (Object.IsValid())
            {
                FString Name;
                if (Object->TryGetStringField(TEXT("name"), Name))
                {
                    FString Type;
                    if (Object->TryGetStringField(TEXT("type"), Type) && !Type.IsEmpty())
                    {
                        Result.Add(FString::Printf(TEXT("%s:%s"), *Type, *Name));
                    }
                    else
                    {
                        Result.Add(Name);
                    }
                }
            }
        }
    }

    return Result.Num() > 0 ? Result : Defaults;
}

TSharedPtr<FJsonObject> SampleRigElementsToJson(
    URigHierarchy* Hierarchy,
    const TArray<FString>& SampleElements,
    TMap<FString, FTransform>& OutTransforms)
{
    TSharedPtr<FJsonObject> PoseObject = MakeShared<FJsonObject>();
    OutTransforms.Reset();

    for (const FString& ElementSpec : SampleElements)
    {
        FRigElementKey ElementKey;
        TSharedPtr<FJsonObject> SampleObject = MakeShared<FJsonObject>();
        SampleObject->SetStringField(TEXT("requested"), ElementSpec);

        if (!ResolveRigElementKey(Hierarchy, ElementSpec, ElementKey))
        {
            SampleObject->SetBoolField(TEXT("valid"), false);
            SampleObject->SetStringField(TEXT("error"), FString::Printf(TEXT("Rig element not found: %s"), *ElementSpec));
            PoseObject->SetObjectField(ElementSpec, SampleObject);
            continue;
        }

        SampleObject->SetBoolField(TEXT("valid"), true);
        SampleObject->SetStringField(TEXT("name"), ElementKey.Name.ToString());
        SampleObject->SetStringField(TEXT("type"), RigElementTypeToString(ElementKey.Type));

        if (ElementKey.Type == ERigElementType::Curve)
        {
            SampleObject->SetNumberField(TEXT("curve_value"), Hierarchy->GetCurveValue(ElementKey));
            SampleObject->SetStringField(TEXT("note"), TEXT("Curve elements do not expose a global transform"));
            PoseObject->SetObjectField(ElementKey.Name.ToString(), SampleObject);
            continue;
        }

        const FTransform GlobalTransform = Hierarchy->GetGlobalTransform(ElementKey, false);
        SampleObject->SetObjectField(TEXT("global"), TransformToJsonObject(GlobalTransform));
        PoseObject->SetObjectField(ElementKey.Name.ToString(), SampleObject);
        OutTransforms.Add(ElementKey.Name.ToString(), GlobalTransform);
    }

    return PoseObject;
}

TSharedPtr<FJsonObject> TransformDeltaToJsonObject(const FTransform& PreTransform, const FTransform& PostTransform)
{
    const FVector TranslationDelta = PostTransform.GetLocation() - PreTransform.GetLocation();
    const FVector ScaleDelta = PostTransform.GetScale3D() - PreTransform.GetScale3D();
    const FQuat PreRotation = PreTransform.GetRotation().GetNormalized();
    const FQuat PostRotation = PostTransform.GetRotation().GetNormalized();

    TSharedPtr<FJsonObject> DeltaObject = MakeShared<FJsonObject>();
    DeltaObject->SetArrayField(TEXT("translation_delta"), VectorToJsonArray(TranslationDelta));
    DeltaObject->SetNumberField(TEXT("translation_distance"), TranslationDelta.Size());
    DeltaObject->SetNumberField(TEXT("rotation_delta_degrees"), FMath::RadiansToDegrees(PreRotation.AngularDistance(PostRotation)));
    DeltaObject->SetArrayField(TEXT("scale_delta"), VectorToJsonArray(ScaleDelta));
    return DeltaObject;
}

TSharedPtr<FJsonObject> BuildRigPoseDeltaObject(
    const TMap<FString, FTransform>& PreTransforms,
    const TMap<FString, FTransform>& PostTransforms)
{
    TSharedPtr<FJsonObject> DeltaObject = MakeShared<FJsonObject>();
    for (const TPair<FString, FTransform>& Pair : PostTransforms)
    {
        const FTransform* PreTransform = PreTransforms.Find(Pair.Key);
        if (!PreTransform)
        {
            continue;
        }

        DeltaObject->SetObjectField(Pair.Key, TransformDeltaToJsonObject(*PreTransform, Pair.Value));
    }
    return DeltaObject;
}

FString BlueprintNodeWorldTypeToString(const UWorld* World)
{
    if (!World)
    {
        return TEXT("None");
    }

    switch (World->WorldType)
    {
    case EWorldType::Editor:
        return TEXT("Editor");
    case EWorldType::PIE:
        return TEXT("PIE");
    case EWorldType::Game:
        return TEXT("Game");
    case EWorldType::GamePreview:
        return TEXT("GamePreview");
    case EWorldType::EditorPreview:
        return TEXT("EditorPreview");
    case EWorldType::Inactive:
        return TEXT("Inactive");
    default:
        return TEXT("Unknown");
    }
}

TArray<UWorld*> GetCandidateWorldsForSkeletalSampling(bool bPreferPIEWorld, bool bAllowEditorWorld = true)
{
    TArray<UWorld*> Worlds;

    auto AddWorld = [&Worlds](UWorld* World)
    {
        if (World && !Worlds.Contains(World))
        {
            Worlds.Add(World);
        }
    };

    if (bPreferPIEWorld && GEngine)
    {
        for (const FWorldContext& WorldContext : GEngine->GetWorldContexts())
        {
            UWorld* World = WorldContext.World();
            if (!World)
            {
                continue;
            }

            if (WorldContext.WorldType == EWorldType::PIE ||
                WorldContext.WorldType == EWorldType::Game ||
                WorldContext.WorldType == EWorldType::GamePreview)
            {
                AddWorld(World);
            }
        }
    }

    if (bAllowEditorWorld && GEditor)
    {
        AddWorld(GEditor->GetEditorWorldContext().World());
    }

    if (!bPreferPIEWorld && GEngine)
    {
        for (const FWorldContext& WorldContext : GEngine->GetWorldContexts())
        {
            UWorld* World = WorldContext.World();
            if (!World)
            {
                continue;
            }

            if (WorldContext.WorldType == EWorldType::PIE ||
                WorldContext.WorldType == EWorldType::Game ||
                WorldContext.WorldType == EWorldType::GamePreview)
            {
                AddWorld(World);
            }
        }
    }

    return Worlds;
}

FString GetActorLabelForSkeletalSampling(const AActor* Actor)
{
    return Actor ? Actor->GetActorLabel() : FString();
}

bool ActorMatchesSkeletalSamplerFilters(
    const AActor* Actor,
    const FString& ActorLabel,
    const FString& ActorName,
    const FString& ActorPath)
{
    if (!IsValid(Actor))
    {
        return false;
    }

    if (!ActorLabel.IsEmpty() && !GetActorLabelForSkeletalSampling(Actor).Equals(ActorLabel, ESearchCase::IgnoreCase))
    {
        return false;
    }

    if (!ActorName.IsEmpty() && !Actor->GetName().Equals(ActorName, ESearchCase::IgnoreCase))
    {
        return false;
    }

    if (!ActorPath.IsEmpty())
    {
        const FString PathName = Actor->GetPathName();
        if (!PathName.Equals(ActorPath, ESearchCase::IgnoreCase) && !PathName.EndsWith(ActorPath, ESearchCase::IgnoreCase))
        {
            return false;
        }
    }

    return true;
}

TArray<AActor*> FindSkeletalSamplerActors(
    UWorld* World,
    const FString& ActorLabel,
    const FString& ActorName,
    const FString& ActorPath)
{
    TArray<AActor*> Actors;
    if (!World)
    {
        return Actors;
    }

    for (TActorIterator<AActor> It(World); It; ++It)
    {
        AActor* Actor = *It;
        if (!ActorMatchesSkeletalSamplerFilters(Actor, ActorLabel, ActorName, ActorPath))
        {
            continue;
        }

        TArray<USkeletalMeshComponent*> Components;
        Actor->GetComponents<USkeletalMeshComponent>(Components);
        if (Components.Num() > 0)
        {
            Actors.Add(Actor);
        }
    }

    return Actors;
}

USkeletalMeshComponent* FindSkeletalSamplerComponent(
    AActor* Actor,
    const FString& ComponentName,
    int32& OutMatchedComponentCount)
{
    OutMatchedComponentCount = 0;
    if (!Actor)
    {
        return nullptr;
    }

    TArray<USkeletalMeshComponent*> Components;
    Actor->GetComponents<USkeletalMeshComponent>(Components);

    USkeletalMeshComponent* FirstValidComponent = nullptr;
    for (USkeletalMeshComponent* Component : Components)
    {
        if (!IsValid(Component))
        {
            continue;
        }

        if (!FirstValidComponent)
        {
            FirstValidComponent = Component;
        }

        if (ComponentName.IsEmpty())
        {
            ++OutMatchedComponentCount;
            continue;
        }

        if (Component->GetName().Equals(ComponentName, ESearchCase::IgnoreCase))
        {
            ++OutMatchedComponentCount;
            return Component;
        }
    }

    return ComponentName.IsEmpty() ? FirstValidComponent : nullptr;
}

TSharedPtr<FJsonObject> ActorToSkeletalSamplerJson(const AActor* Actor)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    if (!Actor)
    {
        return Object;
    }

    Object->SetStringField(TEXT("label"), GetActorLabelForSkeletalSampling(Actor));
    Object->SetStringField(TEXT("name"), Actor->GetName());
    Object->SetStringField(TEXT("path"), Actor->GetPathName());
    Object->SetStringField(TEXT("class"), Actor->GetClass() ? Actor->GetClass()->GetPathName() : FString());
    return Object;
}

FString AnimationModeToString(EAnimationMode::Type AnimationMode)
{
    switch (AnimationMode)
    {
    case EAnimationMode::AnimationBlueprint:
        return TEXT("AnimationBlueprint");
    case EAnimationMode::AnimationSingleNode:
        return TEXT("AnimationSingleNode");
    case EAnimationMode::AnimationCustomMode:
        return TEXT("AnimationCustomMode");
    default:
        return TEXT("Unknown");
    }
}

TSharedPtr<FJsonObject> SkeletalComponentToSamplerJson(USkeletalMeshComponent* Component)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    if (!Component)
    {
        return Object;
    }

    const USkeletalMesh* SkeletalMesh = Component->GetSkeletalMeshAsset();
    const UClass* AnimClass = Component->GetAnimClass();

    Object->SetStringField(TEXT("name"), Component->GetName());
    Object->SetStringField(TEXT("path"), Component->GetPathName());
    Object->SetStringField(TEXT("class"), Component->GetClass() ? Component->GetClass()->GetPathName() : FString());
    Object->SetStringField(TEXT("skeletal_mesh"), SkeletalMesh ? SkeletalMesh->GetPathName() : FString());
    Object->SetStringField(TEXT("anim_class"), AnimClass ? AnimClass->GetPathName() : FString());
    Object->SetStringField(TEXT("animation_mode"), AnimationModeToString(Component->GetAnimationMode()));
    Object->SetObjectField(TEXT("component_transform"), TransformToJsonObject(Component->GetComponentTransform()));
    return Object;
}

TArray<TSharedPtr<FJsonValue>> StringArrayToJsonValues(const TArray<FString>& Strings)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    for (const FString& String : Strings)
    {
        Values.Add(MakeShared<FJsonValueString>(String));
    }
    return Values;
}

TSharedPtr<FJsonObject> SampleBoneTransformToJson(
    const USkeletalMeshComponent* Component,
    const FString& BoneNameText)
{
    TSharedPtr<FJsonObject> SampleObject = MakeShared<FJsonObject>();
    SampleObject->SetStringField(TEXT("name"), BoneNameText);
    SampleObject->SetStringField(TEXT("type"), TEXT("bone"));

    if (!Component)
    {
        SampleObject->SetBoolField(TEXT("valid"), false);
        SampleObject->SetStringField(TEXT("error"), TEXT("SkeletalMeshComponent is null"));
        return SampleObject;
    }

    const FName BoneName(*BoneNameText);
    const int32 BoneIndex = Component->GetBoneIndex(BoneName);
    if (BoneIndex == INDEX_NONE)
    {
        SampleObject->SetBoolField(TEXT("valid"), false);
        SampleObject->SetStringField(TEXT("error"), FString::Printf(TEXT("Bone not found: %s"), *BoneNameText));
        return SampleObject;
    }

    SampleObject->SetBoolField(TEXT("valid"), true);
    SampleObject->SetNumberField(TEXT("bone_index"), BoneIndex);
    SampleObject->SetStringField(TEXT("parent_bone"), Component->GetParentBone(BoneName).ToString());
    SampleObject->SetObjectField(TEXT("world"), TransformToJsonObject(Component->GetSocketTransform(BoneName, RTS_World)));
    SampleObject->SetObjectField(TEXT("component"), TransformToJsonObject(Component->GetSocketTransform(BoneName, RTS_Component)));
    return SampleObject;
}

TSharedPtr<FJsonObject> SampleSocketTransformToJson(
    const USkeletalMeshComponent* Component,
    const FString& SocketNameText)
{
    TSharedPtr<FJsonObject> SampleObject = MakeShared<FJsonObject>();
    SampleObject->SetStringField(TEXT("name"), SocketNameText);
    SampleObject->SetStringField(TEXT("type"), TEXT("socket"));

    if (!Component)
    {
        SampleObject->SetBoolField(TEXT("valid"), false);
        SampleObject->SetStringField(TEXT("error"), TEXT("SkeletalMeshComponent is null"));
        return SampleObject;
    }

    const FName SocketName(*SocketNameText);
    if (!Component->DoesSocketExist(SocketName))
    {
        SampleObject->SetBoolField(TEXT("valid"), false);
        SampleObject->SetStringField(TEXT("error"), FString::Printf(TEXT("Socket not found: %s"), *SocketNameText));
        return SampleObject;
    }

    SampleObject->SetBoolField(TEXT("valid"), true);
    SampleObject->SetStringField(TEXT("socket_bone"), Component->GetSocketBoneName(SocketName).ToString());
    SampleObject->SetObjectField(TEXT("world"), TransformToJsonObject(Component->GetSocketTransform(SocketName, RTS_World)));
    SampleObject->SetObjectField(TEXT("component"), TransformToJsonObject(Component->GetSocketTransform(SocketName, RTS_Component)));
    return SampleObject;
}

int32 GetClampedIntParam(
    const TSharedPtr<FJsonObject>& Params,
    const FString& FieldName,
    int32 DefaultValue,
    int32 MinValue,
    int32 MaxValue)
{
    double Value = static_cast<double>(DefaultValue);
    if (Params.IsValid())
    {
        Params->TryGetNumberField(FieldName, Value);
    }
    return FMath::Clamp(FMath::RoundToInt(Value), MinValue, MaxValue);
}

double GetClampedNumberParam(
    const TSharedPtr<FJsonObject>& Params,
    const FString& FieldName,
    double DefaultValue,
    double MinValue,
    double MaxValue)
{
    double Value = DefaultValue;
    if (Params.IsValid())
    {
        Params->TryGetNumberField(FieldName, Value);
    }
    return FMath::Clamp(Value, MinValue, MaxValue);
}

TSharedPtr<FJsonObject> AnimMontageRuntimeStateToJson(UAnimInstance* AnimInstance)
{
    TSharedPtr<FJsonObject> MontageObject = MakeShared<FJsonObject>();
    if (!AnimInstance)
    {
        MontageObject->SetBoolField(TEXT("valid"), false);
        MontageObject->SetStringField(TEXT("error"), TEXT("AnimInstance is null"));
        return MontageObject;
    }

    UAnimMontage* ActiveMontage = AnimInstance->GetCurrentActiveMontage();
    if (!ActiveMontage)
    {
        MontageObject->SetBoolField(TEXT("valid"), false);
        MontageObject->SetStringField(TEXT("note"), TEXT("No active montage"));
        return MontageObject;
    }

    MontageObject->SetBoolField(TEXT("valid"), true);
    MontageObject->SetStringField(TEXT("name"), ActiveMontage->GetName());
    MontageObject->SetStringField(TEXT("path"), ActiveMontage->GetPathName());
    MontageObject->SetBoolField(TEXT("is_playing"), AnimInstance->Montage_IsPlaying(ActiveMontage));
    MontageObject->SetBoolField(TEXT("is_stopped"), AnimInstance->Montage_GetIsStopped(ActiveMontage));
    MontageObject->SetStringField(TEXT("current_section"), AnimInstance->Montage_GetCurrentSection(ActiveMontage).ToString());
    MontageObject->SetNumberField(TEXT("position"), AnimInstance->Montage_GetPosition(ActiveMontage));
    MontageObject->SetNumberField(TEXT("blend_time"), AnimInstance->Montage_GetBlendTime(ActiveMontage));
    MontageObject->SetNumberField(TEXT("play_rate"), AnimInstance->Montage_GetPlayRate(ActiveMontage));
    MontageObject->SetNumberField(TEXT("effective_play_rate"), AnimInstance->Montage_GetEffectivePlayRate(ActiveMontage));
    return MontageObject;
}

TSharedPtr<FJsonObject> AnimCurvesRuntimeStateToJson(
    UAnimInstance* AnimInstance,
    const TSharedPtr<FJsonObject>& Params,
    TArray<TSharedPtr<FJsonValue>>& WarningValues)
{
    TSharedPtr<FJsonObject> CurvesObject = MakeShared<FJsonObject>();
    if (!AnimInstance)
    {
        CurvesObject->SetBoolField(TEXT("valid"), false);
        CurvesObject->SetStringField(TEXT("error"), TEXT("AnimInstance is null"));
        return CurvesObject;
    }

    const TArray<FString> RequestedCurveNames = GetStringArrayParam(Params, TEXT("curve_names"), TArray<FString>());
    const int32 MaxCurves = GetClampedIntParam(Params, TEXT("max_curves"), 128, 0, 2048);

    TArray<FName> CurveNames;
    if (RequestedCurveNames.Num() > 0)
    {
        for (const FString& CurveNameText : RequestedCurveNames)
        {
            if (!CurveNameText.IsEmpty())
            {
                CurveNames.AddUnique(FName(*CurveNameText));
            }
        }
    }
    else
    {
        AnimInstance->GetAllCurveNames(CurveNames);
    }

    TSharedPtr<FJsonObject> ValuesObject = MakeShared<FJsonObject>();
    int32 AddedCurveCount = 0;
    for (const FName& CurveName : CurveNames)
    {
        if (MaxCurves >= 0 && AddedCurveCount >= MaxCurves)
        {
            break;
        }

        float CurveValue = 0.0f;
        const bool bFound = AnimInstance->GetCurveValue(CurveName, CurveValue);
        TSharedPtr<FJsonObject> CurveObject = MakeShared<FJsonObject>();
        CurveObject->SetBoolField(TEXT("found"), bFound);
        CurveObject->SetNumberField(TEXT("value"), CurveValue);
        ValuesObject->SetObjectField(CurveName.ToString(), CurveObject);
        ++AddedCurveCount;

        if (!bFound && RequestedCurveNames.Num() > 0)
        {
            WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("Curve not found: %s"), *CurveName.ToString())));
        }
    }

    CurvesObject->SetBoolField(TEXT("valid"), true);
    CurvesObject->SetBoolField(TEXT("requested_only"), RequestedCurveNames.Num() > 0);
    CurvesObject->SetNumberField(TEXT("available_or_requested_count"), CurveNames.Num());
    CurvesObject->SetNumberField(TEXT("included_count"), AddedCurveCount);
    CurvesObject->SetBoolField(TEXT("truncated"), CurveNames.Num() > AddedCurveCount);
    CurvesObject->SetObjectField(TEXT("values"), ValuesObject);
    return CurvesObject;
}

TSharedPtr<FJsonObject> AnimStateMachineRuntimeStateToJson(
    UAnimInstance* AnimInstance,
    const TSharedPtr<FJsonObject>& Params,
    TArray<TSharedPtr<FJsonValue>>& WarningValues)
{
    TSharedPtr<FJsonObject> StateMachinesObject = MakeShared<FJsonObject>();
    if (!AnimInstance)
    {
        StateMachinesObject->SetBoolField(TEXT("valid"), false);
        StateMachinesObject->SetStringField(TEXT("error"), TEXT("AnimInstance is null"));
        return StateMachinesObject;
    }

    const IAnimClassInterface* AnimClassInterface = IAnimClassInterface::GetFromClass(AnimInstance->GetClass());
    if (!AnimClassInterface)
    {
        StateMachinesObject->SetBoolField(TEXT("valid"), false);
        StateMachinesObject->SetStringField(TEXT("error"), TEXT("AnimInstance class does not implement IAnimClassInterface"));
        return StateMachinesObject;
    }

    const TArray<FBakedAnimationStateMachine>& BakedStateMachines = AnimClassInterface->GetBakedStateMachines();
    const FString StateMachineFilter = GetStringParam(Params, TEXT("state_machine_name"), FString());
    const bool bIncludeStates = GetBoolParam(Params, TEXT("include_states"), true);
    const int32 MaxStateMachines = GetClampedIntParam(Params, TEXT("max_state_machines"), 32, 0, 1024);
    const int32 MaxStatesPerMachine = GetClampedIntParam(Params, TEXT("max_states_per_machine"), 64, 0, 2048);
    const int32 MaxStateMachineInstancesToProbe = GetClampedIntParam(Params, TEXT("max_state_machine_instances_to_probe"), 256, 0, 4096);

    TArray<TSharedPtr<FJsonValue>> MachineValues;
    int32 IncludedMachineCount = 0;
    int32 MatchingMachineCount = 0;

    for (int32 MachineInstanceIndex = 0; MachineInstanceIndex < MaxStateMachineInstancesToProbe; ++MachineInstanceIndex)
    {
        const FAnimNode_StateMachine* MachineInstance = AnimInstance->GetStateMachineInstance(MachineInstanceIndex);
        if (!MachineInstance)
        {
            continue;
        }

        const int32 MachineIndexInClass = MachineInstance->StateMachineIndexInClass;
        const FBakedAnimationStateMachine* BakedMachine = BakedStateMachines.IsValidIndex(MachineIndexInClass)
            ? &BakedStateMachines[MachineIndexInClass]
            : nullptr;
        const FString MachineName = BakedMachine
            ? BakedMachine->MachineName.ToString()
            : FString::Printf(TEXT("<unknown_state_machine_%d>"), MachineIndexInClass);

        if (!StateMachineFilter.IsEmpty() && !MachineName.Contains(StateMachineFilter, ESearchCase::IgnoreCase))
        {
            continue;
        }

        ++MatchingMachineCount;
        if (IncludedMachineCount >= MaxStateMachines)
        {
            continue;
        }

        const int32 CurrentStateIndex = MachineInstance->GetCurrentState();
        FName CurrentStateName = NAME_None;
        if (BakedMachine && BakedMachine->States.IsValidIndex(CurrentStateIndex))
        {
            CurrentStateName = BakedMachine->States[CurrentStateIndex].StateName;
        }

        TSharedPtr<FJsonObject> MachineObject = MakeShared<FJsonObject>();
        MachineObject->SetNumberField(TEXT("machine_instance_index"), MachineInstanceIndex);
        MachineObject->SetNumberField(TEXT("machine_index_in_class"), MachineIndexInClass);
        MachineObject->SetStringField(TEXT("machine_name"), MachineName);
        MachineObject->SetStringField(TEXT("current_state_name"), CurrentStateName.ToString());
        MachineObject->SetNumberField(TEXT("current_state_index"), CurrentStateIndex);
        MachineObject->SetNumberField(TEXT("current_state_elapsed_time"), MachineInstance->GetCurrentStateElapsedTime());
        MachineObject->SetBoolField(TEXT("has_baked_state_machine"), BakedMachine != nullptr);
        if (BakedMachine)
        {
            MachineObject->SetNumberField(TEXT("state_count"), BakedMachine->States.Num());
            MachineObject->SetNumberField(TEXT("transition_count"), BakedMachine->Transitions.Num());
            MachineObject->SetNumberField(TEXT("initial_state_index"), BakedMachine->InitialState);
            if (BakedMachine->States.IsValidIndex(BakedMachine->InitialState))
            {
                MachineObject->SetStringField(TEXT("initial_state_name"), BakedMachine->States[BakedMachine->InitialState].StateName.ToString());
            }
        }
        else
        {
            MachineObject->SetNumberField(TEXT("state_count"), 0);
            MachineObject->SetNumberField(TEXT("transition_count"), 0);
            WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
                TEXT("State machine runtime instance %d has no matching baked state machine for class index %d"),
                MachineInstanceIndex,
                MachineIndexInClass)));
        }

        if (bIncludeStates && BakedMachine)
        {
            TArray<TSharedPtr<FJsonValue>> StateValues;
            const int32 StateLimit = FMath::Min(MaxStatesPerMachine, BakedMachine->States.Num());
            for (int32 StateIndex = 0; StateIndex < StateLimit; ++StateIndex)
            {
                const FBakedAnimationState& BakedState = BakedMachine->States[StateIndex];
                TSharedPtr<FJsonObject> StateObject = MakeShared<FJsonObject>();
                StateObject->SetNumberField(TEXT("state_index"), StateIndex);
                StateObject->SetStringField(TEXT("state_name"), BakedState.StateName.ToString());
                StateObject->SetBoolField(TEXT("is_current"), StateIndex == CurrentStateIndex);
                StateObject->SetBoolField(TEXT("is_conduit"), BakedState.bIsAConduit);
                StateObject->SetBoolField(TEXT("always_reset_on_entry"), BakedState.bAlwaysResetOnEntry);
                StateValues.Add(MakeShared<FJsonValueObject>(StateObject));
            }
            MachineObject->SetArrayField(TEXT("states"), StateValues);
            MachineObject->SetNumberField(TEXT("included_state_count"), StateLimit);
            MachineObject->SetBoolField(TEXT("states_truncated"), BakedMachine->States.Num() > StateLimit);
        }

        MachineValues.Add(MakeShared<FJsonValueObject>(MachineObject));
        ++IncludedMachineCount;
    }

    if (!StateMachineFilter.IsEmpty() && MatchingMachineCount == 0)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("No state machine matched filter: %s"), *StateMachineFilter)));
    }

    StateMachinesObject->SetBoolField(TEXT("valid"), true);
    StateMachinesObject->SetStringField(TEXT("state_machine_filter"), StateMachineFilter);
    StateMachinesObject->SetNumberField(TEXT("available_count"), BakedStateMachines.Num());
    StateMachinesObject->SetNumberField(TEXT("max_state_machine_instances_to_probe"), MaxStateMachineInstancesToProbe);
    StateMachinesObject->SetNumberField(TEXT("matching_count"), MatchingMachineCount);
    StateMachinesObject->SetNumberField(TEXT("included_count"), IncludedMachineCount);
    StateMachinesObject->SetBoolField(TEXT("truncated"), MatchingMachineCount > IncludedMachineCount);
    StateMachinesObject->SetStringField(TEXT("runtime_index_note"), TEXT("State machines are read through FAnimNode_StateMachine runtime instances and mapped back with StateMachineIndexInClass. Per-state weights and relevant animation timing are intentionally omitted in this safe MVP."));
    StateMachinesObject->SetArrayField(TEXT("machines"), MachineValues);
    return StateMachinesObject;
}

struct FAnimInstanceRuntimeTarget
{
    AActor* Actor = nullptr;
    USkeletalMeshComponent* Component = nullptr;
    UAnimInstance* AnimInstance = nullptr;
    UWorld* World = nullptr;
    int32 MatchedActorCount = 0;
    int32 MatchedComponentCount = 0;
    FString ActorLabel;
    FString ActorName;
    FString ActorPath;
    FString ComponentName;
};

struct FAnimInstanceRuntimePropertyAssignment
{
    FString Name;
    TSharedPtr<FJsonValue> Value;
};

struct FAnimStateRuntimeResponseCase
{
    FString Name;
    TArray<FAnimInstanceRuntimePropertyAssignment> Assignments;
    int32 TickCount = 0;
    double TickDeltaTime = 1.0 / 30.0;
    bool bRestoreAfterCase = true;
};

TSharedPtr<FJsonObject> AnimInstanceToRuntimeJson(UAnimInstance* AnimInstance)
{
    TSharedPtr<FJsonObject> AnimInstanceObject = MakeShared<FJsonObject>();
    if (!AnimInstance)
    {
        return AnimInstanceObject;
    }

    AnimInstanceObject->SetStringField(TEXT("name"), AnimInstance->GetName());
    AnimInstanceObject->SetStringField(TEXT("path"), AnimInstance->GetPathName());
    AnimInstanceObject->SetStringField(TEXT("class"), AnimInstance->GetClass() ? AnimInstance->GetClass()->GetPathName() : FString());
    AnimInstanceObject->SetStringField(TEXT("outer"), AnimInstance->GetOuter() ? AnimInstance->GetOuter()->GetPathName() : FString());
    return AnimInstanceObject;
}

bool FindAnimInstanceRuntimeTarget(
    const TSharedPtr<FJsonObject>& Params,
    bool bPreferPIEWorld,
    bool bRequirePIEWorld,
    const FString& ActionText,
    FAnimInstanceRuntimeTarget& OutTarget,
    TArray<TSharedPtr<FJsonValue>>& WarningValues,
    FString& OutError)
{
    OutError.Reset();
    OutTarget = FAnimInstanceRuntimeTarget();
    OutTarget.ActorLabel = GetStringParam(Params, TEXT("actor_label"), FString());
    OutTarget.ActorName = GetStringParam(Params, TEXT("actor_name"), FString());
    OutTarget.ActorPath = GetStringParam(Params, TEXT("actor_path"), FString());
    OutTarget.ComponentName = GetStringParam(Params, TEXT("component_name"), FString());

    const TArray<UWorld*> CandidateWorlds = GetCandidateWorldsForSkeletalSampling(bPreferPIEWorld, !bRequirePIEWorld);
    for (UWorld* World : CandidateWorlds)
    {
        const TArray<AActor*> Actors = FindSkeletalSamplerActors(World, OutTarget.ActorLabel, OutTarget.ActorName, OutTarget.ActorPath);
        if (Actors.Num() == 0)
        {
            continue;
        }

        OutTarget.MatchedActorCount += Actors.Num();
        for (AActor* Actor : Actors)
        {
            int32 CandidateComponentCount = 0;
            USkeletalMeshComponent* Component = FindSkeletalSamplerComponent(Actor, OutTarget.ComponentName, CandidateComponentCount);
            if (!Component)
            {
                continue;
            }

            OutTarget.Actor = Actor;
            OutTarget.Component = Component;
            OutTarget.World = World;
            OutTarget.MatchedComponentCount = CandidateComponentCount;
            break;
        }

        if (OutTarget.Actor && OutTarget.Component)
        {
            break;
        }
    }

    if (!OutTarget.Actor || !OutTarget.Component || !OutTarget.World)
    {
        OutError = bRequirePIEWorld
            ? FString::Printf(
                TEXT("No SkeletalMeshComponent actor matched actor_label='%s', actor_name='%s', actor_path='%s', component_name='%s' in active PIE/SIE/play worlds"),
                *OutTarget.ActorLabel,
                *OutTarget.ActorName,
                *OutTarget.ActorPath,
                *OutTarget.ComponentName)
            : FString::Printf(
                TEXT("No SkeletalMeshComponent actor matched actor_label='%s', actor_name='%s', actor_path='%s', component_name='%s' in candidate editor/PIE worlds"),
                *OutTarget.ActorLabel,
                *OutTarget.ActorName,
                *OutTarget.ActorPath,
                *OutTarget.ComponentName);
        return false;
    }

    if (OutTarget.MatchedActorCount > 1)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
            TEXT("Matched %d actors; %s the first matching actor in world priority order"),
            OutTarget.MatchedActorCount,
            *ActionText)));
    }

    if (OutTarget.ComponentName.IsEmpty() && OutTarget.MatchedComponentCount > 1)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
            TEXT("Actor has %d SkeletalMeshComponents; %s the first component because component_name was not provided"),
            OutTarget.MatchedComponentCount,
            *ActionText)));
    }

    OutTarget.AnimInstance = OutTarget.Component->GetAnimInstance();
    if (!OutTarget.AnimInstance)
    {
        OutError = FString::Printf(
            TEXT("Matched SkeletalMeshComponent '%s' has no AnimInstance. animation_mode=%s anim_class=%s"),
            *OutTarget.Component->GetName(),
            *AnimationModeToString(OutTarget.Component->GetAnimationMode()),
            OutTarget.Component->GetAnimClass() ? *OutTarget.Component->GetAnimClass()->GetPathName() : TEXT("<none>"));
        return false;
    }

    return true;
}

void PopulateAnimInstanceRuntimeTargetFields(
    TSharedPtr<FJsonObject> ResultObj,
    const FAnimInstanceRuntimeTarget& Target,
    bool bPreferPIEWorld,
    bool bRequirePIEWorld)
{
    ResultObj->SetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    ResultObj->SetBoolField(TEXT("require_pie_world"), bRequirePIEWorld);
    ResultObj->SetBoolField(TEXT("is_play_session_active"), IsBlueprintNodePlaySessionActive());
    ResultObj->SetStringField(TEXT("sampled_world_type"), BlueprintNodeWorldTypeToString(Target.World));
    ResultObj->SetStringField(TEXT("sampled_world_name"), Target.World ? Target.World->GetName() : FString());
    ResultObj->SetNumberField(TEXT("matched_actor_count"), Target.MatchedActorCount);
    ResultObj->SetNumberField(TEXT("matched_component_count"), Target.MatchedComponentCount);
    ResultObj->SetStringField(TEXT("requested_actor_label"), Target.ActorLabel);
    ResultObj->SetStringField(TEXT("requested_actor_name"), Target.ActorName);
    ResultObj->SetStringField(TEXT("requested_actor_path"), Target.ActorPath);
    ResultObj->SetStringField(TEXT("requested_component_name"), Target.ComponentName);
    ResultObj->SetObjectField(TEXT("actor"), ActorToSkeletalSamplerJson(Target.Actor));
    ResultObj->SetObjectField(TEXT("component"), SkeletalComponentToSamplerJson(Target.Component));
    ResultObj->SetObjectField(TEXT("anim_instance"), AnimInstanceToRuntimeJson(Target.AnimInstance));
}

void AddAnimInstanceRuntimePropertyAssignment(
    TArray<FAnimInstanceRuntimePropertyAssignment>& Assignments,
    const FString& PropertyName,
    const TSharedPtr<FJsonValue>& Value)
{
    if (!PropertyName.TrimStartAndEnd().IsEmpty() && Value.IsValid())
    {
        FAnimInstanceRuntimePropertyAssignment Assignment;
        Assignment.Name = PropertyName;
        Assignment.Value = Value;
        Assignments.Add(Assignment);
    }
}

void AddJsonObjectFieldsAsAnimInstanceRuntimeAssignments(
    TArray<FAnimInstanceRuntimePropertyAssignment>& Assignments,
    const TSharedPtr<FJsonObject>& Object)
{
    if (!Object.IsValid())
    {
        return;
    }

    for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : Object->Values)
    {
        AddAnimInstanceRuntimePropertyAssignment(Assignments, Pair.Key, Pair.Value);
    }
}

void AddPropertyArrayAsAnimInstanceRuntimeAssignments(
    TArray<FAnimInstanceRuntimePropertyAssignment>& Assignments,
    const TArray<TSharedPtr<FJsonValue>>* PropertyValues)
{
    if (!PropertyValues)
    {
        return;
    }

    for (const TSharedPtr<FJsonValue>& PropertyValue : *PropertyValues)
    {
        if (!PropertyValue.IsValid() || PropertyValue->Type != EJson::Object)
        {
            continue;
        }

        const TSharedPtr<FJsonObject> PropertyObject = PropertyValue->AsObject();
        if (!PropertyObject.IsValid())
        {
            continue;
        }

        FString PropertyName = GetStringParam(PropertyObject, TEXT("name"), FString());
        if (PropertyName.IsEmpty())
        {
            PropertyName = GetStringParam(PropertyObject, TEXT("property_name"), FString());
        }

        AddAnimInstanceRuntimePropertyAssignment(Assignments, PropertyName, PropertyObject->TryGetField(TEXT("value")));
    }
}

TArray<FAnimInstanceRuntimePropertyAssignment> ParseAnimInstanceRuntimePropertyAssignments(const TSharedPtr<FJsonObject>& Params)
{
    TArray<FAnimInstanceRuntimePropertyAssignment> Assignments;
    if (!Params.IsValid())
    {
        return Assignments;
    }

    const TSharedPtr<FJsonObject>* PropertiesObject = nullptr;
    if ((Params->TryGetObjectField(TEXT("properties"), PropertiesObject) || Params->TryGetObjectField(TEXT("property_values"), PropertiesObject)) && PropertiesObject)
    {
        AddJsonObjectFieldsAsAnimInstanceRuntimeAssignments(Assignments, *PropertiesObject);
    }

    const TArray<TSharedPtr<FJsonValue>>* PropertyArray = nullptr;
    if (Params->TryGetArrayField(TEXT("properties"), PropertyArray) || Params->TryGetArrayField(TEXT("property_values"), PropertyArray))
    {
        AddPropertyArrayAsAnimInstanceRuntimeAssignments(Assignments, PropertyArray);
    }

    const FString SinglePropertyName = GetStringParam(Params, TEXT("property_name"), FString());
    if (!SinglePropertyName.IsEmpty())
    {
        AddAnimInstanceRuntimePropertyAssignment(Assignments, SinglePropertyName, Params->TryGetField(TEXT("value")));
    }

    return Assignments;
}

TSharedPtr<FJsonObject> ApplyAnimInstanceRuntimePropertyAssignments(
    UAnimInstance* AnimInstance,
    const TArray<FAnimInstanceRuntimePropertyAssignment>& Assignments,
    bool bIncludePreviousValues,
    TArray<FAnimInstanceRuntimePropertyAssignment>* OutRestoreAssignments,
    TArray<TSharedPtr<FJsonValue>>& ErrorValues)
{
    TSharedPtr<FJsonObject> AppliedObject = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> AssignmentValues;
    int32 SuccessCount = 0;

    for (const FAnimInstanceRuntimePropertyAssignment& Assignment : Assignments)
    {
        TSharedPtr<FJsonObject> AssignmentObject = MakeShared<FJsonObject>();
        AssignmentObject->SetStringField(TEXT("name"), Assignment.Name);
        AssignmentObject->SetField(TEXT("requested_value"), Assignment.Value.IsValid() ? Assignment.Value : MakeShared<FJsonValueNull>());

        FProperty* Property = AnimInstance && AnimInstance->GetClass()
            ? AnimInstance->GetClass()->FindPropertyByName(FName(*Assignment.Name))
            : nullptr;
        if (Property)
        {
            AssignmentObject->SetStringField(TEXT("property_type"), Property->GetClass() ? Property->GetClass()->GetName() : FString());
            AssignmentObject->SetNumberField(TEXT("property_flags"), static_cast<double>(Property->PropertyFlags));
        }

        TSharedPtr<FJsonValue> PreviousValue = GetUObjectPropertyJson(AnimInstance, Assignment.Name);
        if (bIncludePreviousValues)
        {
            AssignmentObject->SetField(TEXT("previous_value"), PreviousValue);
        }

        FString PropertyError;
        if (SetUObjectPropertyFromJson(AnimInstance, Assignment.Name, Assignment.Value, PropertyError))
        {
            ++SuccessCount;
            AssignmentObject->SetBoolField(TEXT("success"), true);
            AssignmentObject->SetField(TEXT("echo_value"), GetUObjectPropertyJson(AnimInstance, Assignment.Name));

            if (OutRestoreAssignments)
            {
                FAnimInstanceRuntimePropertyAssignment RestoreAssignment;
                RestoreAssignment.Name = Assignment.Name;
                RestoreAssignment.Value = PreviousValue;
                OutRestoreAssignments->Add(RestoreAssignment);
            }
        }
        else
        {
            AssignmentObject->SetBoolField(TEXT("success"), false);
            AssignmentObject->SetStringField(TEXT("error"), PropertyError);
            ErrorValues.Add(MakeShared<FJsonValueString>(PropertyError));
        }

        AssignmentValues.Add(MakeShared<FJsonValueObject>(AssignmentObject));
    }

    AppliedObject->SetNumberField(TEXT("requested_count"), Assignments.Num());
    AppliedObject->SetNumberField(TEXT("success_count"), SuccessCount);
    AppliedObject->SetBoolField(TEXT("all_succeeded"), SuccessCount == Assignments.Num());
    AppliedObject->SetArrayField(TEXT("assignments"), AssignmentValues);
    return AppliedObject;
}

TSharedPtr<FJsonObject> TickSkeletalComponentForAnimRuntimeProbe(
    USkeletalMeshComponent* Component,
    int32 TickCount,
    double TickDeltaTime,
    bool bRefreshBoneTransforms,
    TArray<TSharedPtr<FJsonValue>>& WarningValues)
{
    TSharedPtr<FJsonObject> TickObject = MakeShared<FJsonObject>();
    TickObject->SetStringField(TEXT("tick_method"), TEXT("USkeletalMeshComponent::TickAnimation"));
    TickObject->SetNumberField(TEXT("requested_tick_count"), TickCount);
    TickObject->SetNumberField(TEXT("tick_delta_time"), TickDeltaTime);
    TickObject->SetBoolField(TEXT("refresh_bone_transforms"), bRefreshBoneTransforms);

    if (!Component)
    {
        TickObject->SetBoolField(TEXT("success"), false);
        TickObject->SetStringField(TEXT("error"), TEXT("SkeletalMeshComponent is null"));
        return TickObject;
    }

    int32 ExecutedTickCount = 0;
    for (int32 TickIndex = 0; TickIndex < TickCount; ++TickIndex)
    {
        Component->TickAnimation(static_cast<float>(TickDeltaTime), false);
        if (bRefreshBoneTransforms)
        {
            Component->RefreshBoneTransforms();
        }
        ++ExecutedTickCount;
    }

    if (TickCount > 0 && !Component->ShouldTickAnimation())
    {
        WarningValues.Add(MakeShared<FJsonValueString>(TEXT("SkeletalMeshComponent::ShouldTickAnimation returned false; forced TickAnimation was still called for the probe")));
    }

    TickObject->SetBoolField(TEXT("success"), true);
    TickObject->SetNumberField(TEXT("executed_tick_count"), ExecutedTickCount);
    return TickObject;
}

TSharedPtr<FJsonObject> CaptureAnimInstanceRuntimeSnapshot(
    UAnimInstance* AnimInstance,
    const TSharedPtr<FJsonObject>& Params,
    TArray<TSharedPtr<FJsonValue>>& WarningValues)
{
    TSharedPtr<FJsonObject> SnapshotObject = MakeShared<FJsonObject>();
    SnapshotObject->SetObjectField(TEXT("anim_instance"), AnimInstanceToRuntimeJson(AnimInstance));
    SnapshotObject->SetObjectField(TEXT("state_machines"), AnimStateMachineRuntimeStateToJson(AnimInstance, Params, WarningValues));

    if (GetBoolParam(Params, TEXT("include_montages"), true))
    {
        SnapshotObject->SetObjectField(TEXT("active_montage"), AnimMontageRuntimeStateToJson(AnimInstance));
    }

    if (GetBoolParam(Params, TEXT("include_curves"), false))
    {
        SnapshotObject->SetObjectField(TEXT("curves"), AnimCurvesRuntimeStateToJson(AnimInstance, Params, WarningValues));
    }

    return SnapshotObject;
}

TArray<FAnimStateRuntimeResponseCase> ParseAnimStateRuntimeResponseCases(
    const TSharedPtr<FJsonObject>& Params,
    int32 DefaultTickCount,
    double DefaultTickDeltaTime,
    bool bDefaultRestoreAfterCase)
{
    TArray<FAnimStateRuntimeResponseCase> Cases;
    if (!Params.IsValid())
    {
        return Cases;
    }

    const TArray<TSharedPtr<FJsonValue>>* CaseValues = nullptr;
    if (Params->TryGetArrayField(TEXT("cases"), CaseValues) && CaseValues && CaseValues->Num() > 0)
    {
        for (int32 CaseIndex = 0; CaseIndex < CaseValues->Num(); ++CaseIndex)
        {
            const TSharedPtr<FJsonValue>& CaseValue = (*CaseValues)[CaseIndex];
            if (!CaseValue.IsValid() || CaseValue->Type != EJson::Object)
            {
                continue;
            }

            const TSharedPtr<FJsonObject> CaseObject = CaseValue->AsObject();
            if (!CaseObject.IsValid())
            {
                continue;
            }

            FAnimStateRuntimeResponseCase RuntimeCase;
            RuntimeCase.Name = GetStringParam(CaseObject, TEXT("name"), FString::Printf(TEXT("case_%d"), CaseIndex));
            RuntimeCase.Assignments = ParseAnimInstanceRuntimePropertyAssignments(CaseObject);
            RuntimeCase.TickCount = GetClampedIntParam(CaseObject, TEXT("tick_count"), DefaultTickCount, 0, 240);
            RuntimeCase.TickDeltaTime = GetClampedNumberParam(CaseObject, TEXT("tick_delta_time"), DefaultTickDeltaTime, 0.0, 1.0);
            RuntimeCase.bRestoreAfterCase = GetBoolParam(CaseObject, TEXT("restore_after_case"), bDefaultRestoreAfterCase);
            Cases.Add(RuntimeCase);
        }
    }

    if (Cases.Num() == 0)
    {
        FAnimStateRuntimeResponseCase RuntimeCase;
        RuntimeCase.Name = GetStringParam(Params, TEXT("name"), TEXT("case_0"));
        RuntimeCase.Assignments = ParseAnimInstanceRuntimePropertyAssignments(Params);
        RuntimeCase.TickCount = DefaultTickCount;
        RuntimeCase.TickDeltaTime = DefaultTickDeltaTime;
        RuntimeCase.bRestoreAfterCase = bDefaultRestoreAfterCase;
        Cases.Add(RuntimeCase);
    }

    return Cases;
}

UControlRig* CreateTransientControlRigFromParams(
    const TSharedPtr<FJsonObject>& Params,
    FString& OutAssetPath,
    FString& OutClassPath,
    FString& OutError)
{
    OutAssetPath.Reset();
    OutClassPath.Reset();
    OutError.Reset();

    FString ControlRigClassPath;
    Params->TryGetStringField(TEXT("control_rig_class"), ControlRigClassPath);

    FString ControlRigPath;
    if (!Params->TryGetStringField(TEXT("control_rig_path"), ControlRigPath))
    {
        Params->TryGetStringField(TEXT("control_rig_asset"), ControlRigPath);
    }
    if (ControlRigPath.IsEmpty())
    {
        Params->TryGetStringField(TEXT("control_rig"), ControlRigPath);
    }

    UControlRigBlueprint* ControlRigBlueprint = nullptr;
    UClass* ControlRigClass = nullptr;

    if (!ControlRigClassPath.TrimStartAndEnd().IsEmpty())
    {
        ControlRigClass = LoadClassForPin(ControlRigClassPath);
        if (!ControlRigClass || !ControlRigClass->IsChildOf(UControlRig::StaticClass()))
        {
            OutError = FString::Printf(TEXT("ControlRig class not found or invalid: %s"), *ControlRigClassPath);
            return nullptr;
        }
        OutClassPath = ControlRigClass->GetPathName();
    }
    else if (!ControlRigPath.TrimStartAndEnd().IsEmpty())
    {
        UObject* ControlRigObject = LoadObjectForPin(ControlRigPath);
        ControlRigBlueprint = Cast<UControlRigBlueprint>(ControlRigObject);
        if (ControlRigBlueprint)
        {
            ControlRigClass = ControlRigBlueprint->GetControlRigClass();
            OutAssetPath = ControlRigBlueprint->GetPathName();
            OutClassPath = ControlRigClass ? ControlRigClass->GetPathName() : FString();
        }
        else
        {
            ControlRigClass = Cast<UClass>(ControlRigObject);
            if (!ControlRigClass && ControlRigObject)
            {
                ControlRigClass = ControlRigObject->GetClass();
            }
            if (!ControlRigClass || !ControlRigClass->IsChildOf(UControlRig::StaticClass()))
            {
                OutError = FString::Printf(TEXT("ControlRig asset/class not found or invalid: %s"), *ControlRigPath);
                return nullptr;
            }
            OutAssetPath = ControlRigObject ? ControlRigObject->GetPathName() : FString();
            OutClassPath = ControlRigClass->GetPathName();
        }
    }
    else
    {
        OutError = TEXT("Missing 'control_rig_path' or 'control_rig_class' parameter");
        return nullptr;
    }

    if (!ControlRigClass)
    {
        OutError = TEXT("Failed to resolve ControlRig generated class");
        return nullptr;
    }

    UControlRig* ControlRig = ControlRigBlueprint ? ControlRigBlueprint->CreateControlRig() : NewObject<UControlRig>(GetTransientPackage(), ControlRigClass);
    if (!ControlRig)
    {
        OutError = FString::Printf(TEXT("Failed to create transient ControlRig instance from %s"), *ControlRigClass->GetPathName());
        return nullptr;
    }

    return ControlRig;
}

bool ParseRigidBodySimulationSpace(const FString& RawValue, ESimulationSpace& OutSimulationSpace)
{
    const FString Value = RawValue.TrimStartAndEnd().Replace(TEXT(" "), TEXT(""));
    if (Value.Equals(TEXT("ComponentSpace"), ESearchCase::IgnoreCase))
    {
        OutSimulationSpace = ESimulationSpace::ComponentSpace;
        return true;
    }
    if (Value.Equals(TEXT("WorldSpace"), ESearchCase::IgnoreCase))
    {
        OutSimulationSpace = ESimulationSpace::WorldSpace;
        return true;
    }
    if (Value.Equals(TEXT("BaseBoneSpace"), ESearchCase::IgnoreCase))
    {
        OutSimulationSpace = ESimulationSpace::BaseBoneSpace;
        return true;
    }
    return false;
}

FString GetRigidBodySimulationSpaceName(ESimulationSpace SimulationSpace)
{
    switch (SimulationSpace)
    {
    case ESimulationSpace::ComponentSpace:
        return TEXT("ComponentSpace");
    case ESimulationSpace::WorldSpace:
        return TEXT("WorldSpace");
    case ESimulationSpace::BaseBoneSpace:
        return TEXT("BaseBoneSpace");
    default:
        return TEXT("Unknown");
    }
}

bool ParseTrailChainBoneAxis(const FString& RawValue, EAxis::Type& OutAxis)
{
    const FString Value = RawValue.TrimStartAndEnd().Replace(TEXT(" "), TEXT("")).Replace(TEXT("_"), TEXT(""));
    if (Value.Equals(TEXT("X"), ESearchCase::IgnoreCase) || Value.Equals(TEXT("EAxisX"), ESearchCase::IgnoreCase))
    {
        OutAxis = EAxis::X;
        return true;
    }
    if (Value.Equals(TEXT("Y"), ESearchCase::IgnoreCase) || Value.Equals(TEXT("EAxisY"), ESearchCase::IgnoreCase))
    {
        OutAxis = EAxis::Y;
        return true;
    }
    if (Value.Equals(TEXT("Z"), ESearchCase::IgnoreCase) || Value.Equals(TEXT("EAxisZ"), ESearchCase::IgnoreCase))
    {
        OutAxis = EAxis::Z;
        return true;
    }
    return false;
}

FString GetTrailChainBoneAxisName(EAxis::Type Axis)
{
    switch (Axis)
    {
    case EAxis::X:
        return TEXT("X");
    case EAxis::Y:
        return TEXT("Y");
    case EAxis::Z:
        return TEXT("Z");
    default:
        return TEXT("None");
    }
}

bool ParseModifyCurveApplyMode(const FString& RawValue, EModifyCurveApplyMode& OutApplyMode)
{
    const FString Value = RawValue.TrimStartAndEnd().Replace(TEXT(" "), TEXT("")).Replace(TEXT("_"), TEXT(""));
    if (Value.Equals(TEXT("Add"), ESearchCase::IgnoreCase))
    {
        OutApplyMode = EModifyCurveApplyMode::Add;
        return true;
    }
    if (Value.Equals(TEXT("Scale"), ESearchCase::IgnoreCase))
    {
        OutApplyMode = EModifyCurveApplyMode::Scale;
        return true;
    }
    if (Value.Equals(TEXT("Blend"), ESearchCase::IgnoreCase))
    {
        OutApplyMode = EModifyCurveApplyMode::Blend;
        return true;
    }
    if (Value.Equals(TEXT("WeightedMovingAverage"), ESearchCase::IgnoreCase) || Value.Equals(TEXT("WMA"), ESearchCase::IgnoreCase))
    {
        OutApplyMode = EModifyCurveApplyMode::WeightedMovingAverage;
        return true;
    }
    if (Value.Equals(TEXT("RemapCurve"), ESearchCase::IgnoreCase) || Value.Equals(TEXT("Remap"), ESearchCase::IgnoreCase))
    {
        OutApplyMode = EModifyCurveApplyMode::RemapCurve;
        return true;
    }
    return false;
}

FString GetModifyCurveApplyModeName(EModifyCurveApplyMode ApplyMode)
{
    switch (ApplyMode)
    {
    case EModifyCurveApplyMode::Add:
        return TEXT("Add");
    case EModifyCurveApplyMode::Scale:
        return TEXT("Scale");
    case EModifyCurveApplyMode::Blend:
        return TEXT("Blend");
    case EModifyCurveApplyMode::WeightedMovingAverage:
        return TEXT("WeightedMovingAverage");
    case EModifyCurveApplyMode::RemapCurve:
        return TEXT("RemapCurve");
    default:
        return TEXT("Unknown");
    }
}

void UpsertModifyCurveEntry(TArray<TPair<FName, float>>& Entries, const FName& CurveName, float CurveValue)
{
    if (CurveName.IsNone())
    {
        return;
    }

    for (TPair<FName, float>& Entry : Entries)
    {
        if (Entry.Key == CurveName)
        {
            Entry.Value = CurveValue;
            return;
        }
    }

    Entries.Emplace(CurveName, CurveValue);
}

TArray<TPair<FName, float>> BuildDefaultModifyCurveEntries()
{
    TArray<TPair<FName, float>> Entries;
    Entries.Emplace(FName(TEXT("IK_blend_interact")), 1.0f);
    Entries.Emplace(FName(TEXT("IKBlend_l")), 1.0f);
    return Entries;
}

void SortModifyCurveEntries(TArray<TPair<FName, float>>& Entries)
{
    Entries.Sort([](const TPair<FName, float>& A, const TPair<FName, float>& B)
    {
        return A.Key.LexicalLess(B.Key);
    });
}

TArray<TPair<FName, float>> ParseModifyCurveEntries(const TSharedPtr<FJsonObject>& Params, FString& OutError)
{
    OutError.Reset();
    if (!Params.IsValid())
    {
        return BuildDefaultModifyCurveEntries();
    }

    TArray<TPair<FName, float>> Entries;
    const TSharedPtr<FJsonObject>* CurveObject = nullptr;
    if (Params->TryGetObjectField(TEXT("curve_values"), CurveObject) || Params->TryGetObjectField(TEXT("curves"), CurveObject))
    {
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : (*CurveObject)->Values)
        {
            if (!Pair.Value.IsValid() || Pair.Value->Type != EJson::Number)
            {
                OutError = FString::Printf(TEXT("Curve '%s' value must be numeric"), *Pair.Key);
                return TArray<TPair<FName, float>>();
            }
            UpsertModifyCurveEntry(Entries, FName(*Pair.Key), static_cast<float>(Pair.Value->AsNumber()));
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* CurveArray = nullptr;
    if (Params->TryGetArrayField(TEXT("curve_values"), CurveArray) || Params->TryGetArrayField(TEXT("curves"), CurveArray))
    {
        for (const TSharedPtr<FJsonValue>& Value : *CurveArray)
        {
            if (!Value.IsValid() || Value->Type != EJson::Object)
            {
                OutError = TEXT("Curve array entries must be objects with 'name' and 'value'");
                return TArray<TPair<FName, float>>();
            }

            const TSharedPtr<FJsonObject> EntryObject = Value->AsObject();
            FString NameText;
            double CurveValue = 0.0;
            if (!EntryObject->TryGetStringField(TEXT("name"), NameText) || NameText.TrimStartAndEnd().IsEmpty())
            {
                OutError = TEXT("Curve array entry is missing non-empty 'name'");
                return TArray<TPair<FName, float>>();
            }
            if (!EntryObject->TryGetNumberField(TEXT("value"), CurveValue))
            {
                OutError = FString::Printf(TEXT("Curve array entry '%s' is missing numeric 'value'"), *NameText);
                return TArray<TPair<FName, float>>();
            }

            UpsertModifyCurveEntry(Entries, FName(*NameText.TrimStartAndEnd()), static_cast<float>(CurveValue));
        }
    }

    if (Entries.Num() == 0)
    {
        Entries = BuildDefaultModifyCurveEntries();
    }

    SortModifyCurveEntries(Entries);
    return Entries;
}

TSharedPtr<FJsonObject> ModifyCurveEntriesToJsonObject(const TArray<TPair<FName, float>>& Entries)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    for (const TPair<FName, float>& Entry : Entries)
    {
        Object->SetNumberField(Entry.Key.ToString(), Entry.Value);
    }
    return Object;
}

FAnimNode_ModifyCurve* GetMutableModifyCurveAnimNode(UAnimGraphNode_ModifyCurve* ModifyCurveNode)
{
    if (!ModifyCurveNode)
    {
        return nullptr;
    }

    FStructProperty* NodeProperty = ModifyCurveNode->GetFNodeProperty();
    if (!NodeProperty || NodeProperty->Struct != FAnimNode_ModifyCurve::StaticStruct())
    {
        return nullptr;
    }

    return NodeProperty->ContainerPtrToValuePtr<FAnimNode_ModifyCurve>(ModifyCurveNode);
}

bool ModifyCurveEntriesMatchNode(const FAnimNode_ModifyCurve* ModifyCurveNode, const TArray<TPair<FName, float>>& Entries)
{
    if (!ModifyCurveNode)
    {
        return false;
    }

    if (ModifyCurveNode->CurveNames.Num() != Entries.Num() ||
        ModifyCurveNode->CurveValues.Num() != Entries.Num() ||
        ModifyCurveNode->CurveMap.Num() != Entries.Num())
    {
        return false;
    }

    for (int32 Index = 0; Index < Entries.Num(); ++Index)
    {
        if (ModifyCurveNode->CurveNames[Index] != Entries[Index].Key ||
            !FMath::IsNearlyEqual(ModifyCurveNode->CurveValues[Index], Entries[Index].Value, KINDA_SMALL_NUMBER))
        {
            return false;
        }

        const float* MapValue = ModifyCurveNode->CurveMap.Find(Entries[Index].Key);
        if (!MapValue || !FMath::IsNearlyEqual(*MapValue, Entries[Index].Value, KINDA_SMALL_NUMBER))
        {
            return false;
        }
    }

    return true;
}

struct FControlRigInputDefaultRequest
{
    FName PropertyName;
    TSharedPtr<FJsonValue> Value;
};

void UpsertControlRigInputDefault(TArray<FControlRigInputDefaultRequest>& Requests, const FName& PropertyName, const TSharedPtr<FJsonValue>& Value)
{
    if (PropertyName.IsNone() || !Value.IsValid())
    {
        return;
    }

    for (FControlRigInputDefaultRequest& Request : Requests)
    {
        if (Request.PropertyName == PropertyName)
        {
            Request.Value = Value;
            return;
        }
    }

    FControlRigInputDefaultRequest Request;
    Request.PropertyName = PropertyName;
    Request.Value = Value;
    Requests.Add(Request);
}

TArray<FControlRigInputDefaultRequest> BuildDefaultControlRigInputDefaults()
{
    TArray<FControlRigInputDefaultRequest> Requests;
    UpsertControlRigInputDefault(Requests, FName(TEXT("ShouldDoIKTrace")), MakeShared<FJsonValueBoolean>(true));
    UpsertControlRigInputDefault(Requests, FName(TEXT("InteractionWorldLocation")), VectorToJsonValue(FVector(80.0, -40.0, 80.0)));
    return Requests;
}

void SortControlRigInputDefaults(TArray<FControlRigInputDefaultRequest>& Requests)
{
    Requests.Sort([](const FControlRigInputDefaultRequest& A, const FControlRigInputDefaultRequest& B)
    {
        return A.PropertyName.LexicalLess(B.PropertyName);
    });
}

TArray<FControlRigInputDefaultRequest> ParseControlRigInputDefaults(const TSharedPtr<FJsonObject>& Params, FString& OutError)
{
    OutError.Reset();
    if (!Params.IsValid())
    {
        return BuildDefaultControlRigInputDefaults();
    }

    TArray<FControlRigInputDefaultRequest> Requests;
    const TSharedPtr<FJsonObject>* DefaultsObject = nullptr;
    if (Params->TryGetObjectField(TEXT("input_defaults"), DefaultsObject) || Params->TryGetObjectField(TEXT("defaults"), DefaultsObject))
    {
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : (*DefaultsObject)->Values)
        {
            if (!Pair.Value.IsValid())
            {
                OutError = FString::Printf(TEXT("Input default '%s' has an invalid value"), *Pair.Key);
                return TArray<FControlRigInputDefaultRequest>();
            }
            UpsertControlRigInputDefault(Requests, FName(*Pair.Key), Pair.Value);
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* DefaultsArray = nullptr;
    if (Params->TryGetArrayField(TEXT("input_defaults"), DefaultsArray) || Params->TryGetArrayField(TEXT("defaults"), DefaultsArray))
    {
        for (const TSharedPtr<FJsonValue>& Value : *DefaultsArray)
        {
            if (!Value.IsValid() || Value->Type != EJson::Object)
            {
                OutError = TEXT("Input default array entries must be objects with 'name' and 'value'");
                return TArray<FControlRigInputDefaultRequest>();
            }

            const TSharedPtr<FJsonObject> EntryObject = Value->AsObject();
            FString NameText;
            if (!EntryObject->TryGetStringField(TEXT("name"), NameText) || NameText.TrimStartAndEnd().IsEmpty())
            {
                OutError = TEXT("Input default array entry is missing non-empty 'name'");
                return TArray<FControlRigInputDefaultRequest>();
            }

            TSharedPtr<FJsonValue> EntryValue = EntryObject->TryGetField(TEXT("value"));
            if (!EntryValue.IsValid())
            {
                OutError = FString::Printf(TEXT("Input default '%s' is missing 'value'"), *NameText);
                return TArray<FControlRigInputDefaultRequest>();
            }

            UpsertControlRigInputDefault(Requests, FName(*NameText.TrimStartAndEnd()), EntryValue);
        }
    }

    if (Requests.Num() == 0)
    {
        Requests = BuildDefaultControlRigInputDefaults();
    }

    SortControlRigInputDefaults(Requests);
    return Requests;
}

TSharedPtr<FJsonObject> ControlRigInputDefaultsToJsonObject(const TArray<FControlRigInputDefaultRequest>& Requests)
{
    TSharedPtr<FJsonObject> Object = MakeShared<FJsonObject>();
    for (const FControlRigInputDefaultRequest& Request : Requests)
    {
        Object->SetField(Request.PropertyName.ToString(), Request.Value);
    }
    return Object;
}

FAnimNode_ControlRig* GetMutableControlRigAnimNode(UAnimGraphNode_ControlRig* ControlRigNode)
{
    if (!ControlRigNode)
    {
        return nullptr;
    }

    FStructProperty* NodeProperty = ControlRigNode->GetFNodeProperty();
    if (!NodeProperty || NodeProperty->Struct != FAnimNode_ControlRig::StaticStruct())
    {
        return nullptr;
    }

    return NodeProperty->ContainerPtrToValuePtr<FAnimNode_ControlRig>(ControlRigNode);
}

FString GetControlRigClassPathFromNode(UAnimGraphNode_ControlRig* ControlRigNode)
{
    FAnimNode_ControlRig* ControlRigAnimNode = GetMutableControlRigAnimNode(ControlRigNode);
    if (!ControlRigAnimNode)
    {
        return FString();
    }

    FClassProperty* ControlRigClassProperty = FindFProperty<FClassProperty>(FAnimNode_ControlRig::StaticStruct(), TEXT("ControlRigClass"));
    if (!ControlRigClassProperty)
    {
        return FString();
    }

    UClass* ControlRigClass = Cast<UClass>(ControlRigClassProperty->GetObjectPropertyValue_InContainer(ControlRigAnimNode));
    return ControlRigClass ? ControlRigClass->GetPathName() : FString();
}

TArray<FName> GetControlRigCustomPinNamesByReflection(UAnimGraphNode_ControlRig* ControlRigNode)
{
    TArray<FName> Names;
    if (!ControlRigNode)
    {
        return Names;
    }

    FArrayProperty* CustomPinPropertiesProperty = FindFProperty<FArrayProperty>(ControlRigNode->GetClass(), TEXT("CustomPinProperties"));
    FStructProperty* OptionalPinStructProperty = CustomPinPropertiesProperty ? CastField<FStructProperty>(CustomPinPropertiesProperty->Inner) : nullptr;
    if (!CustomPinPropertiesProperty || !OptionalPinStructProperty)
    {
        return Names;
    }

    FNameProperty* PropertyNameProperty = FindFProperty<FNameProperty>(OptionalPinStructProperty->Struct, TEXT("PropertyName"));
    if (!PropertyNameProperty)
    {
        return Names;
    }

    FScriptArrayHelper ArrayHelper(CustomPinPropertiesProperty, CustomPinPropertiesProperty->ContainerPtrToValuePtr<void>(ControlRigNode));
    for (int32 Index = 0; Index < ArrayHelper.Num(); ++Index)
    {
        const void* EntryPtr = ArrayHelper.GetRawPtr(Index);
        const FName PropertyName = PropertyNameProperty->GetPropertyValue_InContainer(EntryPtr);
        if (!PropertyName.IsNone())
        {
            Names.Add(PropertyName);
        }
    }

    Names.Sort([](const FName& A, const FName& B)
    {
        return A.LexicalLess(B);
    });
    return Names;
}

TArray<TSharedPtr<FJsonValue>> NamesToJsonArray(const TArray<FName>& Names)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    for (const FName& Name : Names)
    {
        Values.Add(MakeShared<FJsonValueString>(Name.ToString()));
    }
    return Values;
}

bool SetControlRigCustomPinVisibleByReflection(UAnimGraphNode_ControlRig* ControlRigNode, const FName& PropertyName, bool bVisible, bool& bOutFound, bool& bOutChanged, FString& OutError)
{
    bOutFound = false;
    bOutChanged = false;
    OutError.Reset();

    if (!ControlRigNode)
    {
        OutError = TEXT("ControlRig node is null");
        return false;
    }

    FArrayProperty* CustomPinPropertiesProperty = FindFProperty<FArrayProperty>(ControlRigNode->GetClass(), TEXT("CustomPinProperties"));
    FStructProperty* OptionalPinStructProperty = CustomPinPropertiesProperty ? CastField<FStructProperty>(CustomPinPropertiesProperty->Inner) : nullptr;
    if (!CustomPinPropertiesProperty || !OptionalPinStructProperty)
    {
        OutError = TEXT("Failed to resolve ControlRig CustomPinProperties");
        return false;
    }

    FNameProperty* PropertyNameProperty = FindFProperty<FNameProperty>(OptionalPinStructProperty->Struct, TEXT("PropertyName"));
    FBoolProperty* ShowPinProperty = FindFProperty<FBoolProperty>(OptionalPinStructProperty->Struct, TEXT("bShowPin"));
    if (!PropertyNameProperty || !ShowPinProperty)
    {
        OutError = TEXT("Failed to resolve ControlRig optional pin fields");
        return false;
    }

    FScriptArrayHelper ArrayHelper(CustomPinPropertiesProperty, CustomPinPropertiesProperty->ContainerPtrToValuePtr<void>(ControlRigNode));
    for (int32 Index = 0; Index < ArrayHelper.Num(); ++Index)
    {
        void* EntryPtr = ArrayHelper.GetRawPtr(Index);
        const FName EntryPropertyName = PropertyNameProperty->GetPropertyValue_InContainer(EntryPtr);
        if (EntryPropertyName == PropertyName)
        {
            bOutFound = true;
            const bool bCurrentVisible = ShowPinProperty->GetPropertyValue_InContainer(EntryPtr);
            if (bCurrentVisible != bVisible)
            {
                ShowPinProperty->SetPropertyValue_InContainer(EntryPtr, bVisible);
                bOutChanged = true;
            }
            return true;
        }
    }

    return true;
}

UEdGraphPin* FindControlRigInputPin(UAnimGraphNode_ControlRig* ControlRigNode, const FName& PropertyName)
{
    if (!ControlRigNode)
    {
        return nullptr;
    }

    for (UEdGraphPin* Pin : ControlRigNode->Pins)
    {
        if (!Pin || Pin->Direction != EGPD_Input || Pin->ParentPin || UAnimationGraphSchema::IsPosePin(Pin->PinType))
        {
            continue;
        }

        if (Pin->GetFName() == PropertyName || Pin->PinFriendlyName.ToString().Equals(PropertyName.ToString(), ESearchCase::CaseSensitive))
        {
            return Pin;
        }
    }

    return nullptr;
}

bool TryParseVectorDefaultString(const FString& DefaultString, FVector& OutVector)
{
    const FString Trimmed = DefaultString.TrimStartAndEnd().TrimChar(TEXT('(')).TrimChar(TEXT(')')).TrimStartAndEnd();

    FVector VectorValue = FVector::ZeroVector;
    if (VectorValue.InitFromString(Trimmed))
    {
        OutVector = VectorValue;
        return true;
    }

    TArray<FString> Parts;
    Trimmed.ParseIntoArray(Parts, TEXT(","), true);
    if (Parts.Num() != 3)
    {
        return false;
    }

    double X = 0.0;
    double Y = 0.0;
    double Z = 0.0;
    if (!LexTryParseString(X, *Parts[0].TrimStartAndEnd()) ||
        !LexTryParseString(Y, *Parts[1].TrimStartAndEnd()) ||
        !LexTryParseString(Z, *Parts[2].TrimStartAndEnd()))
    {
        return false;
    }

    OutVector = FVector(X, Y, Z);
    return true;
}

bool TryParseBoolDefaultString(const FString& DefaultString, bool& bOutValue)
{
    const FString Trimmed = DefaultString.TrimStartAndEnd();
    if (Trimmed.Equals(TEXT("true"), ESearchCase::IgnoreCase) || Trimmed == TEXT("1"))
    {
        bOutValue = true;
        return true;
    }
    if (Trimmed.Equals(TEXT("false"), ESearchCase::IgnoreCase) || Trimmed == TEXT("0"))
    {
        bOutValue = false;
        return true;
    }
    return false;
}

bool PinDefaultSemanticallyMatchesJsonValue(
    UEdGraphPin* Pin,
    const TSharedPtr<FJsonValue>& Value,
    const UEdGraphSchema_K2* K2Schema,
    FString& OutRequestedDefaultValue)
{
    OutRequestedDefaultValue.Reset();
    if (!Pin || !Value.IsValid())
    {
        return false;
    }

    if (Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct &&
        Pin->PinType.PinSubCategoryObject == TBaseStructure<FVector>::Get())
    {
        FVector RequestedVector = FVector::ZeroVector;
        FVector CurrentVector = FVector::ZeroVector;
        if (JsonValueToVector(Value, RequestedVector) &&
            TryParseVectorDefaultString(Pin->GetDefaultAsString(), CurrentVector))
        {
            OutRequestedDefaultValue = FString::Printf(TEXT("(X=%s,Y=%s,Z=%s)"),
                *FString::SanitizeFloat(RequestedVector.X),
                *FString::SanitizeFloat(RequestedVector.Y),
                *FString::SanitizeFloat(RequestedVector.Z));
            return CurrentVector.Equals(RequestedVector, KINDA_SMALL_NUMBER);
        }
    }

    if (Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Boolean && Value->Type == EJson::Boolean)
    {
        bool bCurrentValue = false;
        if (TryParseBoolDefaultString(Pin->GetDefaultAsString(), bCurrentValue))
        {
            OutRequestedDefaultValue = Value->AsBool() ? TEXT("true") : TEXT("false");
            return bCurrentValue == Value->AsBool();
        }
    }

    if (K2Schema)
    {
        FString DefaultResolveError;
        if (GetPinDefaultStringForTypeChecked(Value, Pin->PinType, OutRequestedDefaultValue, DefaultResolveError))
        {
            return K2Schema->DoesDefaultValueMatch(*Pin, OutRequestedDefaultValue);
        }
    }

    return false;
}

UAnimGraphNode_ControlRig* ResolveControlRigNodeForInputDefaults(UEdGraph* Graph, const TSharedPtr<FJsonObject>& Params, int32& OutCandidateCount, FString& OutError)
{
    OutCandidateCount = 0;
    OutError.Reset();
    if (!Graph)
    {
        OutError = TEXT("Graph is null");
        return nullptr;
    }

    FString NodeId;
    FString NodeName;
    FString TitleContains;
    FString ControlRigClassFilter;
    if (Params.IsValid())
    {
        Params->TryGetStringField(TEXT("node_id"), NodeId);
        Params->TryGetStringField(TEXT("node_name"), NodeName);
        Params->TryGetStringField(TEXT("title_contains"), TitleContains);
        Params->TryGetStringField(TEXT("control_rig_class"), ControlRigClassFilter);
    }

    TArray<UAnimGraphNode_ControlRig*> Candidates;
    for (UEdGraphNode* Node : Graph->Nodes)
    {
        UAnimGraphNode_ControlRig* ControlRigNode = Cast<UAnimGraphNode_ControlRig>(Node);
        if (!ControlRigNode)
        {
            continue;
        }

        ++OutCandidateCount;

        if (!NodeId.IsEmpty() &&
            !ControlRigNode->NodeGuid.ToString().Equals(NodeId, ESearchCase::IgnoreCase) &&
            !ControlRigNode->GetName().Equals(NodeId, ESearchCase::IgnoreCase))
        {
            continue;
        }
        if (!NodeName.IsEmpty() && !ControlRigNode->GetName().Equals(NodeName, ESearchCase::IgnoreCase))
        {
            continue;
        }
        if (!TitleContains.IsEmpty() && !static_cast<UEdGraphNode*>(ControlRigNode)->GetNodeTitle(ENodeTitleType::FullTitle).ToString().Contains(TitleContains))
        {
            continue;
        }
        if (!ControlRigClassFilter.IsEmpty())
        {
            const FString ClassPath = GetControlRigClassPathFromNode(ControlRigNode);
            if (!ClassPath.Equals(ControlRigClassFilter, ESearchCase::IgnoreCase) &&
                !ClassPath.Contains(ControlRigClassFilter))
            {
                continue;
            }
        }

        Candidates.Add(ControlRigNode);
    }

    if (Candidates.Num() == 0)
    {
        OutError = OutCandidateCount == 0
            ? FString::Printf(TEXT("No ControlRig nodes found in graph '%s'"), *Graph->GetName())
            : FString::Printf(TEXT("No ControlRig node matched the supplied filters in graph '%s'"), *Graph->GetName());
        return nullptr;
    }

    return Candidates[0];
}

bool MatchesNodeFilter(UEdGraphNode* Node, const FString& NodeType, const FString& TitleContains)
{
    if (!Node)
    {
        return false;
    }

    if (!NodeType.IsEmpty())
    {
        const FString ClassName = Node->GetClass()->GetName();
        const FString NodeTitle = Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString();
        if (!ClassName.Contains(NodeType) && !NodeTitle.Contains(NodeType))
        {
            return false;
        }
    }

    if (!TitleContains.IsEmpty() && !Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString().Contains(TitleContains))
    {
        return false;
    }

    return true;
}

FName GetMathFunctionName(const FString& Operation)
{
    if (Operation.Equals(TEXT("add"), ESearchCase::IgnoreCase) || Operation.Equals(TEXT("+"), ESearchCase::IgnoreCase))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Add_DoubleDouble);
    }
    if (Operation.Equals(TEXT("subtract"), ESearchCase::IgnoreCase) || Operation.Equals(TEXT("-"), ESearchCase::IgnoreCase))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Subtract_DoubleDouble);
    }
    if (Operation.Equals(TEXT("multiply"), ESearchCase::IgnoreCase) || Operation.Equals(TEXT("*"), ESearchCase::IgnoreCase))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Multiply_DoubleDouble);
    }
    if (Operation.Equals(TEXT("divide"), ESearchCase::IgnoreCase) || Operation.Equals(TEXT("/"), ESearchCase::IgnoreCase))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Divide_DoubleDouble);
    }
    if (Operation.Equals(TEXT("clamp"), ESearchCase::IgnoreCase))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, FClamp);
    }
    if (Operation.Equals(TEXT("in_range"), ESearchCase::IgnoreCase) || Operation.Equals(TEXT("inrange"), ESearchCase::IgnoreCase))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, InRange_FloatFloat);
    }

    return NAME_None;
}

bool IsOperationAlias(const FString& Operation, std::initializer_list<const TCHAR*> Aliases)
{
    FString NormalizedOperation = Operation.ToLower();
    NormalizedOperation.TrimStartAndEndInline();
    NormalizedOperation.ReplaceInline(TEXT(" "), TEXT("_"));
    NormalizedOperation.ReplaceInline(TEXT("-"), TEXT("_"));

    for (const TCHAR* Alias : Aliases)
    {
        FString NormalizedAlias(Alias);
        NormalizedAlias.ToLowerInline();
        NormalizedAlias.ReplaceInline(TEXT(" "), TEXT("_"));
        NormalizedAlias.ReplaceInline(TEXT("-"), TEXT("_"));
        if (NormalizedOperation == NormalizedAlias)
        {
            return true;
        }
    }

    return false;
}

FName GetCompareFunctionName(const FString& Operation, const FString& ValueType, FString& OutError)
{
    const FString NormalizedType = NormalizeTypeName(ValueType);
    const bool bLess = IsOperationAlias(Operation, {TEXT("less"), TEXT("lt"), TEXT("<")});
    const bool bGreater = IsOperationAlias(Operation, {TEXT("greater"), TEXT("gt"), TEXT(">")});
    const bool bLessEqual = IsOperationAlias(Operation, {TEXT("less_equal"), TEXT("lessequal"), TEXT("le"), TEXT("<=")});
    const bool bGreaterEqual = IsOperationAlias(Operation, {TEXT("greater_equal"), TEXT("greaterequal"), TEXT("ge"), TEXT(">=")});
    const bool bEqual = IsOperationAlias(Operation, {TEXT("equal"), TEXT("equals"), TEXT("eq"), TEXT("==")});
    const bool bNotEqual = IsOperationAlias(Operation, {TEXT("not_equal"), TEXT("notequal"), TEXT("ne"), TEXT("!=")});

    if (!bLess && !bGreater && !bLessEqual && !bGreaterEqual && !bEqual && !bNotEqual)
    {
        OutError = FString::Printf(TEXT("Unsupported compare operation: %s"), *Operation);
        return NAME_None;
    }

    if (NormalizedType == TEXT("int") || NormalizedType == TEXT("integer"))
    {
        if (bLess) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Less_IntInt); }
        if (bGreater) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Greater_IntInt); }
        if (bLessEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, LessEqual_IntInt); }
        if (bGreaterEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, GreaterEqual_IntInt); }
        if (bEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_IntInt); }
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_IntInt);
    }
    if (NormalizedType == TEXT("int64") || NormalizedType == TEXT("integer64"))
    {
        if (bLess) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Less_Int64Int64); }
        if (bGreater) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Greater_Int64Int64); }
        if (bLessEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, LessEqual_Int64Int64); }
        if (bGreaterEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, GreaterEqual_Int64Int64); }
        if (bEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_Int64Int64); }
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_Int64Int64);
    }
    if (NormalizedType == TEXT("float") || NormalizedType == TEXT("double") || NormalizedType == TEXT("real"))
    {
        if (bLess) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Less_DoubleDouble); }
        if (bGreater) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Greater_DoubleDouble); }
        if (bLessEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, LessEqual_DoubleDouble); }
        if (bGreaterEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, GreaterEqual_DoubleDouble); }
        if (bEqual) { return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_DoubleDouble); }
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_DoubleDouble);
    }

    if (bEqual || bNotEqual)
    {
        if (NormalizedType == TEXT("bool") || NormalizedType == TEXT("boolean"))
        {
            return bEqual
                ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_BoolBool)
                : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_BoolBool);
        }
        if (NormalizedType == TEXT("object"))
        {
            return bEqual
                ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_ObjectObject)
                : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_ObjectObject);
        }
        if (NormalizedType == TEXT("class"))
        {
            return bEqual
                ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_ClassClass)
                : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_ClassClass);
        }
        if (NormalizedType == TEXT("name"))
        {
            return bEqual
                ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_NameName)
                : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_NameName);
        }
    }

    OutError = FString::Printf(TEXT("Unsupported compare type/operation combination: type=%s, operation=%s"), *ValueType, *Operation);
    return NAME_None;
}

FName GetBooleanFunctionName(const FString& Operation, FString& OutError)
{
    if (IsOperationAlias(Operation, {TEXT("not"), TEXT("!")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, Not_PreBool);
    }
    if (IsOperationAlias(Operation, {TEXT("and"), TEXT("&&")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BooleanAND);
    }
    if (IsOperationAlias(Operation, {TEXT("nand")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BooleanNAND);
    }
    if (IsOperationAlias(Operation, {TEXT("or"), TEXT("||")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BooleanOR);
    }
    if (IsOperationAlias(Operation, {TEXT("xor")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BooleanXOR);
    }
    if (IsOperationAlias(Operation, {TEXT("nor")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BooleanNOR);
    }
    if (IsOperationAlias(Operation, {TEXT("equal"), TEXT("equals"), TEXT("eq"), TEXT("==")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, EqualEqual_BoolBool);
    }
    if (IsOperationAlias(Operation, {TEXT("not_equal"), TEXT("notequal"), TEXT("ne"), TEXT("!=")}))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, NotEqual_BoolBool);
    }

    OutError = FString::Printf(TEXT("Unsupported boolean operation: %s"), *Operation);
    return NAME_None;
}

FName GetSelectFunctionName(const FString& ValueType, FString& OutError)
{
    const FString NormalizedType = NormalizeTypeName(ValueType);
    if (NormalizedType == TEXT("string"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectString);
    }
    if (NormalizedType == TEXT("text"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectText);
    }
    if (NormalizedType == TEXT("name"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectName);
    }
    if (NormalizedType == TEXT("int") || NormalizedType == TEXT("integer"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectInt);
    }
    if (NormalizedType == TEXT("float") || NormalizedType == TEXT("double") || NormalizedType == TEXT("real"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectFloat);
    }
    if (NormalizedType == TEXT("vector"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectVector);
    }
    if (NormalizedType == TEXT("rotator"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectRotator);
    }
    if (NormalizedType == TEXT("color") || NormalizedType == TEXT("linearcolor"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectColor);
    }
    if (NormalizedType == TEXT("transform"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectTransform);
    }
    if (NormalizedType == TEXT("object"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectObject);
    }
    if (NormalizedType == TEXT("class"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, SelectClass);
    }

    OutError = FString::Printf(TEXT("Unsupported select value type: %s"), *ValueType);
    return NAME_None;
}

FName GetIsValidFunctionName(const FString& ValueType, FString& OutError)
{
    const FString NormalizedType = NormalizeTypeName(ValueType);
    if (NormalizedType.IsEmpty() || NormalizedType == TEXT("object"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, IsValid);
    }
    if (NormalizedType == TEXT("class"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, IsValidClass);
    }

    OutError = FString::Printf(TEXT("Unsupported is_valid value type: %s"), *ValueType);
    return NAME_None;
}

FName GetLiteralFunctionName(const FString& LiteralType, FString& OutError)
{
    const FString NormalizedType = NormalizeTypeName(LiteralType);
    if (NormalizedType == TEXT("int") || NormalizedType == TEXT("integer"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralInt);
    }
    if (NormalizedType == TEXT("int64") || NormalizedType == TEXT("integer64"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralInt64);
    }
    if (NormalizedType == TEXT("float") || NormalizedType == TEXT("single"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralFloat);
    }
    if (NormalizedType == TEXT("double") || NormalizedType == TEXT("real"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralDouble);
    }
    if (NormalizedType == TEXT("bool") || NormalizedType == TEXT("boolean"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralBool);
    }
    if (NormalizedType == TEXT("name"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralName);
    }
    if (NormalizedType == TEXT("byte"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralByte);
    }
    if (NormalizedType == TEXT("string"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralString);
    }
    if (NormalizedType == TEXT("text"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetSystemLibrary, MakeLiteralText);
    }

    OutError = FString::Printf(TEXT("Unsupported literal type: %s"), *LiteralType);
    return NAME_None;
}

FName GetStructHelperFunctionName(const FString& Helper, const FString& StructType, FString& OutError)
{
    const FString NormalizedHelper = NormalizeTypeName(Helper);
    const FString NormalizedStructType = NormalizeTypeName(StructType);
    const bool bMake = NormalizedHelper == TEXT("make");
    const bool bBreak = NormalizedHelper == TEXT("break");

    if (!bMake && !bBreak)
    {
        OutError = FString::Printf(TEXT("Unsupported struct helper operation: %s"), *Helper);
        return NAME_None;
    }

    if (NormalizedStructType == TEXT("vector"))
    {
        return bMake
            ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, MakeVector)
            : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BreakVector);
    }
    if (NormalizedStructType == TEXT("rotator"))
    {
        return bMake
            ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, MakeRotator)
            : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BreakRotator);
    }
    if (NormalizedStructType == TEXT("transform"))
    {
        return bMake
            ? GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, MakeTransform)
            : GET_FUNCTION_NAME_CHECKED(UKismetMathLibrary, BreakTransform);
    }

    OutError = FString::Printf(TEXT("Unsupported native struct helper type: %s"), *StructType);
    return NAME_None;
}

bool TryReadIntegerField(const TSharedPtr<FJsonObject>& Params, const FString& FieldName, int32& OutValue, FString& OutError)
{
    if (!Params.IsValid() || !Params->HasField(FieldName))
    {
        return false;
    }

    const TSharedPtr<FJsonValue> Value = Params->TryGetField(FieldName);
    if (!Value.IsValid() || Value->Type != EJson::Number)
    {
        OutError = FString::Printf(TEXT("'%s' must be a number"), *FieldName);
        return false;
    }

    const double NumberValue = Value->AsNumber();
    const int32 RoundedValue = FMath::RoundToInt(NumberValue);
    if (!FMath::IsNearlyEqual(NumberValue, static_cast<double>(RoundedValue)))
    {
        OutError = FString::Printf(TEXT("'%s' must be an integer"), *FieldName);
        return false;
    }

    OutValue = RoundedValue;
    return true;
}

UEdGraph* ResolveStandardMacroGraph(const FString& MacroName, FString& OutError)
{
    OutError.Reset();
    static const TCHAR* StandardMacroPaths[] = {
        TEXT("/Engine/EditorBlueprintResources/StandardMacros.StandardMacros"),
        TEXT("/Engine/EditorKismetResources/StandardMacros.StandardMacros")
    };

    for (const TCHAR* MacroPath : StandardMacroPaths)
    {
        UBlueprint* MacroBlueprint = LoadObject<UBlueprint>(nullptr, MacroPath);
        if (!MacroBlueprint)
        {
            continue;
        }

        TArray<UEdGraph*> Graphs;
        MacroBlueprint->GetAllGraphs(Graphs);
        for (UEdGraph* Graph : Graphs)
        {
            if (Graph && Graph->GetName().Equals(MacroName, ESearchCase::IgnoreCase))
            {
                return Graph;
            }
        }
    }

    OutError = FString::Printf(TEXT("Standard macro graph not found: %s"), *MacroName);
    return nullptr;
}

FName ResolveLoopMacroName(const FString& LoopType, FString& OutError)
{
    const FString NormalizedLoopType = NormalizeTypeName(LoopType.IsEmpty() ? TEXT("for_loop") : LoopType);
    if (NormalizedLoopType == TEXT("for") || NormalizedLoopType == TEXT("forloop"))
    {
        return TEXT("ForLoop");
    }

    OutError = FString::Printf(TEXT("Unsupported loop_type '%s'. Supported loop_type: for_loop"), *LoopType);
    return NAME_None;
}

bool ApplyOptionalIntegerPinDefault(
    const TSharedPtr<FJsonObject>& Params,
    const FString& FieldName,
    UEdGraphNode* Node,
    const FString& PinName,
    const UEdGraphSchema_K2* K2Schema,
    TSharedPtr<FJsonObject> AppliedDefaults,
    FString& OutError)
{
    if (!Params.IsValid() || !Params->HasField(FieldName))
    {
        return true;
    }

    int32 IntegerValue = 0;
    FString ParseError;
    if (!TryReadIntegerField(Params, FieldName, IntegerValue, ParseError))
    {
        OutError = ParseError.IsEmpty()
            ? FString::Printf(TEXT("Failed to parse integer default field: %s"), *FieldName)
            : ParseError;
        return false;
    }

    UEdGraphPin* Pin = FUnrealMCPCommonUtils::FindPin(Node, PinName, EGPD_Input);
    if (!Pin)
    {
        OutError = FString::Printf(TEXT("Loop pin not found: %s"), *PinName);
        return false;
    }

    FString AppliedValue;
    FString DefaultError;
    if (!ApplyPinDefaultValueChecked(Pin, MakeShared<FJsonValueNumber>(IntegerValue), K2Schema, AppliedValue, DefaultError))
    {
        OutError = FString::Printf(TEXT("Invalid default value for pin '%s': %s"), *PinName, *DefaultError);
        return false;
    }

    if (UK2Node* K2Node = Cast<UK2Node>(Node))
    {
        K2Node->PinDefaultValueChanged(Pin);
    }
    AppliedDefaults->SetStringField(PinName, AppliedValue);
    return true;
}

FName ResolveArrayOperationFunctionName(const FString& Operation, FString& OutError)
{
    const FString NormalizedOperation = NormalizeTypeName(Operation);
    if (NormalizedOperation == TEXT("length") || NormalizedOperation == TEXT("num") || NormalizedOperation == TEXT("count") || NormalizedOperation == TEXT("size"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetArrayLibrary, Array_Length);
    }
    if (NormalizedOperation == TEXT("get"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetArrayLibrary, Array_Get);
    }
    if (NormalizedOperation == TEXT("set") || NormalizedOperation == TEXT("setarrayelem"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetArrayLibrary, Array_Set);
    }
    if (NormalizedOperation == TEXT("add"))
    {
        return GET_FUNCTION_NAME_CHECKED(UKismetArrayLibrary, Array_Add);
    }

    OutError = FString::Printf(TEXT("Unsupported array operation '%s'. Supported operations: length, get, set, add"), *Operation);
    return NAME_None;
}

bool ApplyPinTypeToArrayFunctionNode(UK2Node_CallArrayFunction* ArrayNode, const FEdGraphPinType& ElementPinType, FString& OutError)
{
    if (!ArrayNode)
    {
        OutError = TEXT("Invalid array function node");
        return false;
    }

    UEdGraphPin* TargetArrayPin = ArrayNode->GetTargetArrayPin();
    if (!TargetArrayPin)
    {
        OutError = TEXT("Array function target array pin not found");
        return false;
    }

    TargetArrayPin->PinType.PinCategory = ElementPinType.PinCategory;
    TargetArrayPin->PinType.PinSubCategory = ElementPinType.PinSubCategory;
    TargetArrayPin->PinType.PinSubCategoryObject = ElementPinType.PinSubCategoryObject;
    TargetArrayPin->PinType.ContainerType = EPinContainerType::Array;
    TargetArrayPin->PinType.bIsReference = true;

    UFunction* TargetFunction = ArrayNode->GetTargetFunction();
    if (!TargetFunction)
    {
        OutError = TEXT("Array function target function not found");
        return false;
    }

    const FString& DependentPinsMetadata = TargetFunction->GetMetaData(FBlueprintMetadata::MD_ArrayDependentParam);
    TArray<FString> DependentPinNames;
    DependentPinsMetadata.ParseIntoArray(DependentPinNames, TEXT(","), true);
    for (const FString& DependentPinName : DependentPinNames)
    {
        UEdGraphPin* DependentPin = FUnrealMCPCommonUtils::FindPin(ArrayNode, DependentPinName, EGPD_Input);
        if (!DependentPin)
        {
            DependentPin = FUnrealMCPCommonUtils::FindPin(ArrayNode, DependentPinName, EGPD_Output);
        }
        if (!DependentPin)
        {
            continue;
        }

        DependentPin->PinType.PinCategory = ElementPinType.PinCategory;
        DependentPin->PinType.PinSubCategory = ElementPinType.PinSubCategory;
        DependentPin->PinType.PinSubCategoryObject = ElementPinType.PinSubCategoryObject;
        DependentPin->PinType.ContainerType = EPinContainerType::None;
        DependentPin->PinType.bIsReference = false;
        GetDefault<UEdGraphSchema_K2>()->SetPinAutogeneratedDefaultValueBasedOnType(DependentPin);
    }

    return true;
}

bool ResolveMakeArrayInputs(
    const TSharedPtr<FJsonObject>& Params,
    const TArray<TSharedPtr<FJsonValue>>*& OutValues,
    bool& bOutHasValues,
    int32& OutInputCount,
    FString& OutError)
{
    constexpr int32 MaxInputCount = 128;

    OutValues = nullptr;
    bOutHasValues = false;
    OutInputCount = 1;
    OutError.Reset();

    if (!Params.IsValid())
    {
        OutError = TEXT("Invalid parameters");
        return false;
    }

    if (Params->HasField(TEXT("values")))
    {
        if (!Params->TryGetArrayField(TEXT("values"), OutValues))
        {
            OutError = TEXT("'values' must be an array");
            return false;
        }
        bOutHasValues = true;
        OutInputCount = OutValues ? OutValues->Num() : 0;
    }
    else if (Params->HasField(TEXT("element_defaults")))
    {
        if (!Params->TryGetArrayField(TEXT("element_defaults"), OutValues))
        {
            OutError = TEXT("'element_defaults' must be an array");
            return false;
        }
        bOutHasValues = true;
        OutInputCount = OutValues ? OutValues->Num() : 0;
    }

    if (Params->HasField(TEXT("input_count")))
    {
        int32 ParsedInputCount = 0;
        FString ParseError;
        if (!TryReadIntegerField(Params, TEXT("input_count"), ParsedInputCount, ParseError))
        {
            OutError = ParseError.IsEmpty() ? TEXT("'input_count' must be an integer") : ParseError;
            return false;
        }
        OutInputCount = ParsedInputCount;
    }

    if (OutInputCount < 0 || OutInputCount > MaxInputCount)
    {
        OutError = FString::Printf(TEXT("'input_count' must be between 0 and %d"), MaxInputCount);
        return false;
    }

    if (bOutHasValues && OutValues && OutValues->Num() > OutInputCount)
    {
        OutError = TEXT("'values' cannot contain more entries than 'input_count'");
        return false;
    }

    return true;
}

bool ApplyPinTypeToMakeArrayNode(UK2Node_MakeArray* MakeArrayNode, const FEdGraphPinType& ElementPinType, FString& OutError)
{
    if (!MakeArrayNode)
    {
        OutError = TEXT("Invalid make array node");
        return false;
    }

    UEdGraphPin* OutputPin = MakeArrayNode->GetOutputPin();
    if (!OutputPin)
    {
        OutError = TEXT("Make array output pin not found");
        return false;
    }

    OutputPin->PinType.PinCategory = ElementPinType.PinCategory;
    OutputPin->PinType.PinSubCategory = ElementPinType.PinSubCategory;
    OutputPin->PinType.PinSubCategoryObject = ElementPinType.PinSubCategoryObject;
    OutputPin->PinType.ContainerType = EPinContainerType::Array;
    OutputPin->PinType.PinValueType = FEdGraphTerminalType();
    OutputPin->PinType.bIsReference = false;

    const UEdGraphSchema_K2* K2Schema = GetDefault<UEdGraphSchema_K2>();
    int32 InputPinCount = 0;
    for (UEdGraphPin* Pin : MakeArrayNode->Pins)
    {
        if (!Pin || Pin->Direction != EGPD_Input || Pin->ParentPin)
        {
            continue;
        }

        Pin->PinType.PinCategory = ElementPinType.PinCategory;
        Pin->PinType.PinSubCategory = ElementPinType.PinSubCategory;
        Pin->PinType.PinSubCategoryObject = ElementPinType.PinSubCategoryObject;
        Pin->PinType.ContainerType = EPinContainerType::None;
        Pin->PinType.PinValueType = FEdGraphTerminalType();
        Pin->PinType.bIsReference = false;
        if (K2Schema)
        {
            K2Schema->SetPinAutogeneratedDefaultValueBasedOnType(Pin);
        }
        ++InputPinCount;
    }

    if (InputPinCount != MakeArrayNode->NumInputs)
    {
        OutError = FString::Printf(TEXT("Make array input pin count mismatch. expected=%d actual=%d"), MakeArrayNode->NumInputs, InputPinCount);
        return false;
    }

    return true;
}

bool ResolveSwitchIntCases(const TSharedPtr<FJsonObject>& Params, int32& OutStartIndex, int32& OutCaseCount, FString& OutError)
{
    OutStartIndex = 0;
    OutCaseCount = 2;

    int32 ParsedStartIndex = 0;
    FString ParseError;
    if (TryReadIntegerField(Params, TEXT("start_index"), ParsedStartIndex, ParseError))
    {
        OutStartIndex = ParsedStartIndex;
    }
    else if (!ParseError.IsEmpty())
    {
        OutError = ParseError;
        return false;
    }

    int32 ParsedCaseCount = 2;
    ParseError.Reset();
    if (TryReadIntegerField(Params, TEXT("case_count"), ParsedCaseCount, ParseError))
    {
        OutCaseCount = ParsedCaseCount;
    }
    else if (!ParseError.IsEmpty())
    {
        OutError = ParseError;
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* CaseValues = nullptr;
    if (Params->HasField(TEXT("case_values")) && !Params->TryGetArrayField(TEXT("case_values"), CaseValues))
    {
        OutError = TEXT("'case_values' must be an array");
        return false;
    }

    if (CaseValues)
    {
        if (CaseValues->Num() == 0)
        {
            OutError = TEXT("'case_values' must contain at least one integer case");
            return false;
        }

        TSet<int32> SeenCases;
        int32 PreviousCase = 0;
        for (int32 Index = 0; Index < CaseValues->Num(); ++Index)
        {
            const TSharedPtr<FJsonValue>& CaseValue = (*CaseValues)[Index];
            if (!CaseValue.IsValid() || CaseValue->Type != EJson::Number)
            {
                OutError = TEXT("'case_values' entries must be integers");
                return false;
            }

            const double NumberValue = CaseValue->AsNumber();
            const int32 IntegerValue = FMath::RoundToInt(NumberValue);
            if (!FMath::IsNearlyEqual(NumberValue, static_cast<double>(IntegerValue)))
            {
                OutError = TEXT("'case_values' entries must be integers");
                return false;
            }
            if (SeenCases.Contains(IntegerValue))
            {
                OutError = FString::Printf(TEXT("Duplicate switch int case: %d"), IntegerValue);
                return false;
            }
            SeenCases.Add(IntegerValue);

            if (Index == 0)
            {
                OutStartIndex = IntegerValue;
            }
            else if (IntegerValue != PreviousCase + 1)
            {
                OutError = TEXT("Sparse switch int cases are not supported; use ascending contiguous case values");
                return false;
            }

            PreviousCase = IntegerValue;
        }

        OutCaseCount = CaseValues->Num();
    }

    if (OutCaseCount <= 0)
    {
        OutError = TEXT("'case_count' must be greater than zero");
        return false;
    }
    if (OutCaseCount > 128)
    {
        OutError = TEXT("'case_count' must be 128 or less");
        return false;
    }

    return true;
}

FString NormalizeGraphType(const FString& GraphType)
{
    if (GraphType.IsEmpty())
    {
        return FString();
    }

    FString Normalized = GraphType.ToLower();
    Normalized.ReplaceInline(TEXT(" "), TEXT(""));
    Normalized.ReplaceInline(TEXT("-"), TEXT("_"));

    if (Normalized == TEXT("eventgraph") || Normalized == TEXT("event_graph") || Normalized == TEXT("ubergraph") || Normalized == TEXT("uber_graph"))
    {
        return TEXT("event");
    }
    if (Normalized == TEXT("functiongraph") || Normalized == TEXT("function_graph"))
    {
        return TEXT("function");
    }
    if (Normalized == TEXT("macrograph") || Normalized == TEXT("macro_graph"))
    {
        return TEXT("macro");
    }

    return Normalized;
}

bool BlueprintGraphArrayContains(const TArray<TObjectPtr<UEdGraph>>& GraphArray, const UEdGraph* Graph)
{
    for (const TObjectPtr<UEdGraph>& CandidateGraph : GraphArray)
    {
        if (CandidateGraph.Get() == Graph)
        {
            return true;
        }
    }

    return false;
}

FString GetBlueprintGraphType(const UBlueprint* Blueprint, const UEdGraph* Graph)
{
    if (!Blueprint || !Graph)
    {
        return TEXT("unknown");
    }

    if (BlueprintGraphArrayContains(Blueprint->FunctionGraphs, Graph))
    {
        return TEXT("function");
    }
    if (BlueprintGraphArrayContains(Blueprint->MacroGraphs, Graph))
    {
        return TEXT("macro");
    }
    if (BlueprintGraphArrayContains(Blueprint->UbergraphPages, Graph) || BlueprintGraphArrayContains(Blueprint->EventGraphs, Graph))
    {
        return TEXT("event");
    }
    if (BlueprintGraphArrayContains(Blueprint->DelegateSignatureGraphs, Graph))
    {
        return TEXT("delegate");
    }

    return TEXT("unknown");
}

bool GraphMatchesSelector(const UBlueprint* Blueprint, const UEdGraph* Graph, const FString& GraphId, const FString& GraphName, const FString& GraphType)
{
    if (!Graph)
    {
        return false;
    }

    if (!GraphId.IsEmpty())
    {
        FGuid ParsedGraphId;
        if (FGuid::Parse(GraphId, ParsedGraphId))
        {
            if (Graph->GraphGuid != ParsedGraphId)
            {
                return false;
            }
        }
        else if (Graph->GraphGuid.ToString() != GraphId)
        {
            return false;
        }
    }

    if (!GraphName.IsEmpty() && !Graph->GetName().Equals(GraphName, ESearchCase::IgnoreCase))
    {
        return false;
    }

    const FString NormalizedType = NormalizeGraphType(GraphType);
    if (!NormalizedType.IsEmpty() && NormalizedType != TEXT("any") && GetBlueprintGraphType(Blueprint, Graph) != NormalizedType)
    {
        return false;
    }

    return true;
}

UEdGraph* FindBlueprintGraph(UBlueprint* Blueprint, const FString& GraphId, const FString& GraphName, const FString& GraphType)
{
    if (!Blueprint)
    {
        return nullptr;
    }

    TArray<UEdGraph*> Graphs;
    Blueprint->GetAllGraphs(Graphs);
    for (UEdGraph* Graph : Graphs)
    {
        if (GraphMatchesSelector(Blueprint, Graph, GraphId, GraphName, GraphType))
        {
            return Graph;
        }
    }

    return nullptr;
}

TSharedPtr<FJsonObject> GraphToJson(const UBlueprint* Blueprint, const UEdGraph* Graph)
{
    TSharedPtr<FJsonObject> GraphObject = MakeShared<FJsonObject>();
    if (!Graph)
    {
        return GraphObject;
    }

    GraphObject->SetStringField(TEXT("graph_id"), Graph->GraphGuid.ToString());
    GraphObject->SetStringField(TEXT("graph_name"), Graph->GetName());
    GraphObject->SetStringField(TEXT("graph_type"), GetBlueprintGraphType(Blueprint, Graph));
    GraphObject->SetStringField(TEXT("schema"), Graph->GetSchema() ? Graph->GetSchema()->GetClass()->GetName() : FString());
    GraphObject->SetNumberField(TEXT("node_count"), Graph->Nodes.Num());
    return GraphObject;
}

FMulticastDelegateProperty* FindBlueprintMulticastDelegateProperty(UBlueprint* Blueprint, const FName& DispatcherName)
{
    if (!Blueprint || DispatcherName.IsNone())
    {
        return nullptr;
    }

    TArray<UClass*> CandidateClasses;
    if (Blueprint->SkeletonGeneratedClass)
    {
        CandidateClasses.Add(Blueprint->SkeletonGeneratedClass);
    }
    if (Blueprint->GeneratedClass)
    {
        CandidateClasses.Add(Blueprint->GeneratedClass);
    }
    if (Blueprint->ParentClass)
    {
        CandidateClasses.Add(Blueprint->ParentClass);
    }

    for (UClass* CandidateClass : CandidateClasses)
    {
        if (!CandidateClass)
        {
            continue;
        }

        if (FMulticastDelegateProperty* DelegateProperty = FindFProperty<FMulticastDelegateProperty>(CandidateClass, DispatcherName))
        {
            return DelegateProperty;
        }
    }

    return nullptr;
}

bool IsSelfContextForDelegateProperty(const UBlueprint* Blueprint, const FMulticastDelegateProperty* DelegateProperty)
{
    if (!Blueprint || !DelegateProperty)
    {
        return false;
    }

    const UClass* VariableSourceClass = DelegateProperty->GetOwnerClass();
    return VariableSourceClass == nullptr ||
        (Blueprint->SkeletonGeneratedClass && Blueprint->SkeletonGeneratedClass->IsChildOf(VariableSourceClass));
}

UEdGraph* ResolveBlueprintGraphForNodeCommand(UBlueprint* Blueprint, const TSharedPtr<FJsonObject>& Params, FString& OutError);
void AddGraphField(TSharedPtr<FJsonObject> ResultObj, const UBlueprint* Blueprint, const UEdGraph* Graph);

struct FEventDispatcherNodeRequest
{
    FString BlueprintName;
    FString DispatcherName;
    FVector2D NodePosition = FVector2D(0.0f, 0.0f);
    UBlueprint* Blueprint = nullptr;
    UEdGraph* TargetGraph = nullptr;
    FMulticastDelegateProperty* DelegateProperty = nullptr;
};

bool ResolveEventDispatcherNodeRequest(
    const TSharedPtr<FJsonObject>& Params,
    const TCHAR* ActionName,
    FEventDispatcherNodeRequest& OutRequest,
    FString& OutError)
{
    if (!Params->TryGetStringField(TEXT("blueprint_name"), OutRequest.BlueprintName))
    {
        OutError = TEXT("Missing 'blueprint_name' parameter");
        return false;
    }

    if (!Params->TryGetStringField(TEXT("dispatcher_name"), OutRequest.DispatcherName) &&
        !Params->TryGetStringField(TEXT("event_dispatcher_name"), OutRequest.DispatcherName) &&
        !Params->TryGetStringField(TEXT("delegate_name"), OutRequest.DispatcherName))
    {
        OutError = TEXT("Missing 'dispatcher_name' parameter");
        return false;
    }

    OutRequest.DispatcherName.TrimStartAndEndInline();
    if (OutRequest.DispatcherName.IsEmpty())
    {
        OutError = TEXT("'dispatcher_name' cannot be empty");
        return false;
    }

    if (Params->HasField(TEXT("node_position")))
    {
        OutRequest.NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    OutRequest.Blueprint = FUnrealMCPCommonUtils::FindBlueprint(OutRequest.BlueprintName);
    if (!OutRequest.Blueprint)
    {
        OutError = FString::Printf(TEXT("Blueprint not found: %s"), *OutRequest.BlueprintName);
        return false;
    }

    FString GraphError;
    OutRequest.TargetGraph = ResolveBlueprintGraphForNodeCommand(OutRequest.Blueprint, Params, GraphError);
    if (!OutRequest.TargetGraph)
    {
        OutError = GraphError;
        return false;
    }

    OutRequest.DelegateProperty = FindBlueprintMulticastDelegateProperty(OutRequest.Blueprint, FName(*OutRequest.DispatcherName));
    if (!OutRequest.DelegateProperty)
    {
        OutError = FString::Printf(TEXT("Event dispatcher property not found: %s. Compile or recreate the dispatcher before adding a %s node."), *OutRequest.DispatcherName, ActionName);
        return false;
    }
    if (!OutRequest.DelegateProperty->HasAllPropertyFlags(CPF_BlueprintAssignable))
    {
        OutError = FString::Printf(TEXT("Event dispatcher is not BlueprintAssignable: %s"), *OutRequest.DispatcherName);
        return false;
    }
    if (!OutRequest.DelegateProperty->SignatureFunction)
    {
        OutError = FString::Printf(TEXT("Event dispatcher signature is not available: %s"), *OutRequest.DispatcherName);
        return false;
    }

    return true;
}

template <typename NodeType>
TSharedPtr<FJsonObject> CreateEventDispatcherLifecycleNode(
    const FEventDispatcherNodeRequest& Request,
    const TCHAR* NodeKind,
    bool bAllocatePinsBeforePostPlaced,
    bool bReconstructAfterPostPlaced,
    bool bMarkStructurallyModified)
{
    NodeType* LifecycleNode = NewObject<NodeType>(Request.TargetGraph);
    if (!LifecycleNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to create Event Dispatcher %s node"), NodeKind));
    }

    LifecycleNode->SetFromProperty(
        Request.DelegateProperty,
        IsSelfContextForDelegateProperty(Request.Blueprint, Request.DelegateProperty),
        Request.DelegateProperty->GetOwnerClass());
    if (!LifecycleNode->IsCompatibleWithGraph(Request.TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event Dispatcher %s nodes are not supported in this graph"), NodeKind));
    }

    LifecycleNode->NodePosX = Request.NodePosition.X;
    LifecycleNode->NodePosY = Request.NodePosition.Y;
    Request.TargetGraph->AddNode(LifecycleNode, true);
    LifecycleNode->CreateNewGuid();

    if (bAllocatePinsBeforePostPlaced)
    {
        LifecycleNode->AllocateDefaultPins();
        LifecycleNode->PostPlacedNewNode();
    }
    else
    {
        LifecycleNode->PostPlacedNewNode();
        LifecycleNode->AllocateDefaultPins();
    }

    if (bReconstructAfterPostPlaced)
    {
        LifecycleNode->ReconstructNode();
    }

    if (bMarkStructurallyModified)
    {
        FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Request.Blueprint);
    }
    else
    {
        FBlueprintEditorUtils::MarkBlueprintAsModified(Request.Blueprint);
    }

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(LifecycleNode, true);
    ResultObj->SetStringField(TEXT("dispatcher_name"), Request.DispatcherName);
    ResultObj->SetStringField(TEXT("node_kind"), NodeKind);
    ResultObj->SetStringField(TEXT("signature_function"), Request.DelegateProperty->SignatureFunction->GetPathName());
    AddGraphField(ResultObj, Request.Blueprint, Request.TargetGraph);
    return ResultObj;
}

UEdGraph* CreateBlueprintFunctionGraph(UBlueprint* Blueprint, const FString& RequestedGraphName, FString& OutError)
{
    if (!Blueprint)
    {
        OutError = TEXT("Invalid blueprint");
        return nullptr;
    }
    if (RequestedGraphName.IsEmpty())
    {
        OutError = TEXT("Missing 'graph_name' parameter for function graph creation");
        return nullptr;
    }

    const FName NewGraphName = FBlueprintEditorUtils::FindUniqueKismetName(Blueprint, RequestedGraphName);
    UEdGraph* NewGraph = FBlueprintEditorUtils::CreateNewGraph(
        Blueprint,
        NewGraphName,
        UEdGraph::StaticClass(),
        UEdGraphSchema_K2::StaticClass());

    if (!NewGraph)
    {
        OutError = FString::Printf(TEXT("Failed to create function graph: %s"), *RequestedGraphName);
        return nullptr;
    }

    FBlueprintEditorUtils::AddFunctionGraph<UClass>(Blueprint, NewGraph, true, nullptr);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
    return NewGraph;
}

UEdGraph* ResolveBlueprintGraph(UBlueprint* Blueprint, const TSharedPtr<FJsonObject>& Params, bool bCreateIfMissing, bool& bOutCreated, FString& OutError)
{
    bOutCreated = false;
    OutError.Reset();

    if (!Blueprint)
    {
        OutError = TEXT("Invalid blueprint");
        return nullptr;
    }

    FString GraphId;
    Params->TryGetStringField(TEXT("graph_id"), GraphId);

    FString GraphName;
    Params->TryGetStringField(TEXT("graph_name"), GraphName);

    FString GraphType;
    Params->TryGetStringField(TEXT("graph_type"), GraphType);
    const FString NormalizedType = NormalizeGraphType(GraphType);

    const bool bHasGraphSelector = !GraphId.IsEmpty() || !GraphName.IsEmpty() || !NormalizedType.IsEmpty();
    if (!bHasGraphSelector)
    {
        UEdGraph* EventGraph = FUnrealMCPCommonUtils::FindOrCreateEventGraph(Blueprint);
        if (!EventGraph)
        {
            OutError = TEXT("Failed to get event graph");
        }
        return EventGraph;
    }

    if (UEdGraph* ExistingGraph = FindBlueprintGraph(Blueprint, GraphId, GraphName, GraphType))
    {
        return ExistingGraph;
    }

    if (!bCreateIfMissing)
    {
        OutError = FString::Printf(TEXT("Blueprint graph not found. graph_name='%s', graph_id='%s', graph_type='%s'"), *GraphName, *GraphId, *GraphType);
        return nullptr;
    }

    if (!GraphId.IsEmpty())
    {
        OutError = TEXT("Cannot create a graph with an explicit graph_id");
        return nullptr;
    }

    if (NormalizedType == TEXT("function"))
    {
        UEdGraph* CreatedGraph = CreateBlueprintFunctionGraph(Blueprint, GraphName, OutError);
        bOutCreated = CreatedGraph != nullptr;
        return CreatedGraph;
    }

    if (NormalizedType == TEXT("event") && GraphName.IsEmpty())
    {
        UEdGraph* EventGraph = FUnrealMCPCommonUtils::FindOrCreateEventGraph(Blueprint);
        bOutCreated = EventGraph != nullptr;
        if (!EventGraph)
        {
            OutError = TEXT("Failed to get event graph");
        }
        return EventGraph;
    }

    OutError = FString::Printf(TEXT("Creating graph_type '%s' is not supported by this command"), *GraphType);
    return nullptr;
}

UEdGraph* ResolveBlueprintGraphForNodeCommand(UBlueprint* Blueprint, const TSharedPtr<FJsonObject>& Params, FString& OutError)
{
    bool bCreateIfMissing = false;
    if (Params->HasField(TEXT("create_graph_if_missing")))
    {
        bCreateIfMissing = Params->GetBoolField(TEXT("create_graph_if_missing"));
    }

    bool bCreated = false;
    return ResolveBlueprintGraph(Blueprint, Params, bCreateIfMissing, bCreated, OutError);
}

void AddGraphField(TSharedPtr<FJsonObject> ResultObj, const UBlueprint* Blueprint, const UEdGraph* Graph)
{
    if (ResultObj.IsValid() && Graph)
    {
        ResultObj->SetObjectField(TEXT("graph"), GraphToJson(Blueprint, Graph));
    }
}

template <typename NodeType>
NodeType* AddK2NodeToGraph(UEdGraph* Graph, const FVector2D& NodePosition)
{
    if (!Graph)
    {
        return nullptr;
    }

    NodeType* Node = NewObject<NodeType>(Graph);
    if (!Node)
    {
        return nullptr;
    }

    Node->NodePosX = NodePosition.X;
    Node->NodePosY = NodePosition.Y;
    Graph->AddNode(Node, true);
    Node->CreateNewGuid();
    Node->PostPlacedNewNode();
    Node->AllocateDefaultPins();
    Node->ReconstructNode();
    return Node;
}

bool IsPoseLinkPin(const UEdGraphPin* Pin)
{
    return Pin
        && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct
        && Pin->PinType.PinSubCategoryObject == FPoseLink::StaticStruct();
}

bool IsComponentPoseLinkPin(const UEdGraphPin* Pin)
{
    return Pin
        && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct
        && Pin->PinType.PinSubCategoryObject == FComponentSpacePoseLink::StaticStruct();
}

UEdGraphPin* FindFirstPosePin(UEdGraphNode* Node, EEdGraphPinDirection Direction, const TArray<FString>& PreferredPinNames = TArray<FString>())
{
    if (!Node)
    {
        return nullptr;
    }

    for (const FString& PreferredName : PreferredPinNames)
    {
        for (UEdGraphPin* Pin : Node->Pins)
        {
            if (Pin
                && Pin->Direction == Direction
                && !Pin->ParentPin
                && IsPoseLinkPin(Pin)
                && Pin->PinName.ToString().Equals(PreferredName, ESearchCase::IgnoreCase))
            {
                return Pin;
            }
        }
    }

    for (UEdGraphPin* Pin : Node->Pins)
    {
        if (Pin && Pin->Direction == Direction && !Pin->ParentPin && IsPoseLinkPin(Pin))
        {
            return Pin;
        }
    }

    return nullptr;
}

UAnimGraphNode_ModifyCurve* FindModifyCurveFeedingControlRig(UAnimGraphNode_ControlRig* ControlRigNode)
{
    if (!ControlRigNode)
    {
        return nullptr;
    }

    UEdGraphPin* ControlRigSourceInput = FindFirstPosePin(ControlRigNode, EGPD_Input, { TEXT("Source") });
    if (!ControlRigSourceInput)
    {
        return nullptr;
    }

    for (UEdGraphPin* LinkedPin : ControlRigSourceInput->LinkedTo)
    {
        if (LinkedPin && LinkedPin->GetOwningNode())
        {
            if (UAnimGraphNode_ModifyCurve* ModifyCurveNode = Cast<UAnimGraphNode_ModifyCurve>(LinkedPin->GetOwningNode()))
            {
                return ModifyCurveNode;
            }
        }
    }

    return nullptr;
}

UEdGraphPin* FindFirstComponentPosePin(UEdGraphNode* Node, EEdGraphPinDirection Direction, const TArray<FString>& PreferredPinNames = TArray<FString>())
{
    if (!Node)
    {
        return nullptr;
    }

    for (const FString& PreferredName : PreferredPinNames)
    {
        for (UEdGraphPin* Pin : Node->Pins)
        {
            if (Pin
                && Pin->Direction == Direction
                && !Pin->ParentPin
                && IsComponentPoseLinkPin(Pin)
                && Pin->PinName.ToString().Equals(PreferredName, ESearchCase::IgnoreCase))
            {
                return Pin;
            }
        }
    }

    for (UEdGraphPin* Pin : Node->Pins)
    {
        if (Pin && Pin->Direction == Direction && !Pin->ParentPin && IsComponentPoseLinkPin(Pin))
        {
            return Pin;
        }
    }

    return nullptr;
}

template <typename NodeType>
NodeType* FindFirstNodeOfType(UEdGraph* Graph)
{
    if (!Graph)
    {
        return nullptr;
    }

    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (NodeType* TypedNode = Cast<NodeType>(Node))
        {
            return TypedNode;
        }
    }

    return nullptr;
}

template <typename NodeType>
NodeType* FindFirstNodeOfTypeByName(UEdGraph* Graph, const FString& NodeName)
{
    if (!Graph)
    {
        return nullptr;
    }

    for (UEdGraphNode* Node : Graph->Nodes)
    {
        if (NodeType* TypedNode = Cast<NodeType>(Node))
        {
            if (NodeName.IsEmpty() || TypedNode->GetName().Equals(NodeName, ESearchCase::IgnoreCase))
            {
                return TypedNode;
            }
        }
    }

    return nullptr;
}

template <typename NodeType>
NodeType* AddAnimGraphNodeToGraph(UEdGraph* Graph, const FVector2D& NodePosition)
{
    if (!Graph)
    {
        return nullptr;
    }

    NodeType* Node = NewObject<NodeType>(Graph);
    if (!Node)
    {
        return nullptr;
    }

    Node->NodePosX = NodePosition.X;
    Node->NodePosY = NodePosition.Y;
    Graph->AddNode(Node, true);
    Node->CreateNewGuid();
    Node->PostPlacedNewNode();
    Node->AllocateDefaultPins();
    Node->ReconstructNode();
    return Node;
}

bool IsAnimationGraph(const UEdGraph* Graph)
{
    return Graph
        && Graph->GetSchema()
        && Graph->GetSchema()->GetClass()
        && Graph->GetSchema()->GetClass()->GetName().Contains(TEXT("AnimationGraphSchema"));
}

FString GetAnimNodePrePostMVPKind(UAnimGraphNode_Base* Node)
{
    if (Cast<UAnimGraphNode_RigidBody>(Node))
    {
        return TEXT("rigidbody");
    }
    if (Cast<UAnimGraphNode_Trail>(Node))
    {
        return TEXT("trail");
    }
    if (Cast<UAnimGraphNode_ControlRig>(Node))
    {
        return TEXT("controlrig");
    }
    return TEXT("unsupported");
}

FString GetAnimNodePrePostSupportNote(UAnimGraphNode_Base* Node)
{
    if (Cast<UAnimGraphNode_RigidBody>(Node))
    {
        return TEXT("MVP target for isolated source-vs-output sampling with temporary probe assets.");
    }
    if (Cast<UAnimGraphNode_Trail>(Node))
    {
        return TEXT("MVP target for isolated source-vs-output sampling with safe _MCP_Temp or _MCP_Sample probe assets.");
    }
    if (Cast<UAnimGraphNode_ControlRig>(Node))
    {
        return TEXT("Direct transient ControlRig pre/post probing already exists; compiled AnimGraph-internal ControlRig source-vs-output attribution remains a later instrumentation mode.");
    }
    return TEXT("Dry-run resolver can identify this AnimGraph node, but the isolated runtime sampler MVP does not support it yet.");
}

TArray<TSharedPtr<FJsonValue>> LinkedPinsToJsonValues(const UEdGraphPin* Pin)
{
    TArray<TSharedPtr<FJsonValue>> Values;
    if (!Pin)
    {
        return Values;
    }

    for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
    {
        Values.Add(MakeShared<FJsonValueObject>(PinToJson(LinkedPin)));
    }
    return Values;
}

struct FAnimNodePoseTransformSample
{
    bool bValid = false;
    FTransform WorldTransform = FTransform::Identity;
    FTransform ComponentTransform = FTransform::Identity;
    FString Error;
};

struct FAnimNodePoseCapture
{
    TSharedPtr<FJsonObject> Json = MakeShared<FJsonObject>();
    TMap<FString, FAnimNodePoseTransformSample> BoneSamples;
    TMap<FString, FAnimNodePoseTransformSample> SocketSamples;
};

TArray<FString> GetDefaultAnimNodePrePostSampleBones()
{
    return {
        TEXT("Head_02"),
        TEXT("TailEnd"),
        TEXT("R_Stalk_04"),
        TEXT("L_Stalk_04")
    };
}

FAnimNodePoseTransformSample CaptureBonePoseTransformSample(
    const USkeletalMeshComponent* Component,
    const FString& BoneNameText)
{
    FAnimNodePoseTransformSample Sample;
    if (!Component)
    {
        Sample.Error = TEXT("SkeletalMeshComponent is null");
        return Sample;
    }

    const FName BoneName(*BoneNameText);
    if (Component->GetBoneIndex(BoneName) == INDEX_NONE)
    {
        Sample.Error = FString::Printf(TEXT("Bone not found: %s"), *BoneNameText);
        return Sample;
    }

    Sample.bValid = true;
    Sample.WorldTransform = Component->GetSocketTransform(BoneName, RTS_World);
    Sample.ComponentTransform = Component->GetSocketTransform(BoneName, RTS_Component);
    return Sample;
}

FAnimNodePoseTransformSample CaptureSocketPoseTransformSample(
    const USkeletalMeshComponent* Component,
    const FString& SocketNameText)
{
    FAnimNodePoseTransformSample Sample;
    if (!Component)
    {
        Sample.Error = TEXT("SkeletalMeshComponent is null");
        return Sample;
    }

    const FName SocketName(*SocketNameText);
    if (!Component->DoesSocketExist(SocketName))
    {
        Sample.Error = FString::Printf(TEXT("Socket not found: %s"), *SocketNameText);
        return Sample;
    }

    Sample.bValid = true;
    Sample.WorldTransform = Component->GetSocketTransform(SocketName, RTS_World);
    Sample.ComponentTransform = Component->GetSocketTransform(SocketName, RTS_Component);
    return Sample;
}

FAnimNodePoseCapture CaptureAnimNodeProbePose(
    const USkeletalMeshComponent* Component,
    const TArray<FString>& SampleBones,
    const TArray<FString>& SampleSockets,
    bool bAllowMissingSamples,
    TArray<TSharedPtr<FJsonValue>>& ErrorValues,
    TArray<TSharedPtr<FJsonValue>>& WarningValues)
{
    FAnimNodePoseCapture Capture;
    TSharedPtr<FJsonObject> BoneSamplesObject = MakeShared<FJsonObject>();
    TSharedPtr<FJsonObject> SocketSamplesObject = MakeShared<FJsonObject>();

    for (const FString& BoneName : SampleBones)
    {
        if (BoneName.IsEmpty())
        {
            continue;
        }

        TSharedPtr<FJsonObject> BoneSampleJson = SampleBoneTransformToJson(Component, BoneName);
        FAnimNodePoseTransformSample TransformSample = CaptureBonePoseTransformSample(Component, BoneName);
        Capture.BoneSamples.Add(BoneName, TransformSample);
        if (!TransformSample.bValid)
        {
            const TSharedPtr<FJsonValue> MissingMessage = MakeShared<FJsonValueString>(TransformSample.Error);
            if (bAllowMissingSamples)
            {
                WarningValues.Add(MissingMessage);
            }
            else
            {
                ErrorValues.Add(MissingMessage);
            }
        }
        BoneSamplesObject->SetObjectField(BoneName, BoneSampleJson);
    }

    for (const FString& SocketName : SampleSockets)
    {
        if (SocketName.IsEmpty())
        {
            continue;
        }

        TSharedPtr<FJsonObject> SocketSampleJson = SampleSocketTransformToJson(Component, SocketName);
        FAnimNodePoseTransformSample TransformSample = CaptureSocketPoseTransformSample(Component, SocketName);
        Capture.SocketSamples.Add(SocketName, TransformSample);
        if (!TransformSample.bValid)
        {
            const TSharedPtr<FJsonValue> MissingMessage = MakeShared<FJsonValueString>(TransformSample.Error);
            if (bAllowMissingSamples)
            {
                WarningValues.Add(MissingMessage);
            }
            else
            {
                ErrorValues.Add(MissingMessage);
            }
        }
        SocketSamplesObject->SetObjectField(SocketName, SocketSampleJson);
    }

    Capture.Json->SetObjectField(TEXT("bone_samples"), BoneSamplesObject);
    Capture.Json->SetObjectField(TEXT("socket_samples"), SocketSamplesObject);
    return Capture;
}

TSharedPtr<FJsonObject> TransformDeltaToJson(
    const FAnimNodePoseTransformSample& Before,
    const FAnimNodePoseTransformSample& After)
{
    TSharedPtr<FJsonObject> DeltaObject = MakeShared<FJsonObject>();
    if (!Before.bValid || !After.bValid)
    {
        DeltaObject->SetBoolField(TEXT("valid"), false);
        if (!Before.Error.IsEmpty())
        {
            DeltaObject->SetStringField(TEXT("pre_error"), Before.Error);
        }
        if (!After.Error.IsEmpty())
        {
            DeltaObject->SetStringField(TEXT("post_error"), After.Error);
        }
        return DeltaObject;
    }

    const FVector WorldDelta = After.WorldTransform.GetLocation() - Before.WorldTransform.GetLocation();
    const FVector ComponentDelta = After.ComponentTransform.GetLocation() - Before.ComponentTransform.GetLocation();
    const double WorldRotationDeltaDegrees = FMath::RadiansToDegrees(Before.WorldTransform.GetRotation().AngularDistance(After.WorldTransform.GetRotation()));
    const double ComponentRotationDeltaDegrees = FMath::RadiansToDegrees(Before.ComponentTransform.GetRotation().AngularDistance(After.ComponentTransform.GetRotation()));

    DeltaObject->SetBoolField(TEXT("valid"), true);
    DeltaObject->SetArrayField(TEXT("world_translation_delta"), VectorToJsonArray(WorldDelta));
    DeltaObject->SetNumberField(TEXT("world_translation_distance"), WorldDelta.Size());
    DeltaObject->SetNumberField(TEXT("world_rotation_angle_degrees"), WorldRotationDeltaDegrees);
    DeltaObject->SetArrayField(TEXT("component_translation_delta"), VectorToJsonArray(ComponentDelta));
    DeltaObject->SetNumberField(TEXT("component_translation_distance"), ComponentDelta.Size());
    DeltaObject->SetNumberField(TEXT("component_rotation_angle_degrees"), ComponentRotationDeltaDegrees);
    return DeltaObject;
}

TSharedPtr<FJsonObject> BuildAnimNodePoseDeltas(
    const FAnimNodePoseCapture& Before,
    const FAnimNodePoseCapture& After,
    const TArray<FString>& SampleBones,
    const TArray<FString>& SampleSockets)
{
    TSharedPtr<FJsonObject> DeltaObject = MakeShared<FJsonObject>();
    TSharedPtr<FJsonObject> BoneDeltasObject = MakeShared<FJsonObject>();
    TSharedPtr<FJsonObject> SocketDeltasObject = MakeShared<FJsonObject>();

    for (const FString& BoneName : SampleBones)
    {
        if (BoneName.IsEmpty())
        {
            continue;
        }

        const FAnimNodePoseTransformSample* BeforeSample = Before.BoneSamples.Find(BoneName);
        const FAnimNodePoseTransformSample* AfterSample = After.BoneSamples.Find(BoneName);
        if (BeforeSample && AfterSample)
        {
            BoneDeltasObject->SetObjectField(BoneName, TransformDeltaToJson(*BeforeSample, *AfterSample));
        }
    }

    for (const FString& SocketName : SampleSockets)
    {
        if (SocketName.IsEmpty())
        {
            continue;
        }

        const FAnimNodePoseTransformSample* BeforeSample = Before.SocketSamples.Find(SocketName);
        const FAnimNodePoseTransformSample* AfterSample = After.SocketSamples.Find(SocketName);
        if (BeforeSample && AfterSample)
        {
            SocketDeltasObject->SetObjectField(SocketName, TransformDeltaToJson(*BeforeSample, *AfterSample));
        }
    }

    DeltaObject->SetObjectField(TEXT("bone_deltas"), BoneDeltasObject);
    DeltaObject->SetObjectField(TEXT("socket_deltas"), SocketDeltasObject);
    return DeltaObject;
}

TSharedPtr<FJsonObject> BuildAnimNodePrePostRuntimeTickDeltaResponse(
    const TSharedPtr<FJsonObject>& Params,
    const FString& BlueprintName,
    UBlueprint* Blueprint,
    UEdGraph* TargetGraph,
    UAnimGraphNode_Base* TargetNode,
    const TSharedPtr<FJsonObject>& TargetNodeObject,
    const TArray<FString>& SampleBones,
    const TArray<FString>& SampleSockets,
    bool bIsolatedSamplerSupported)
{
    FString Mode = GetStringParam(Params, TEXT("mode"), TEXT("active_component_tick_delta"));
    Mode.TrimStartAndEndInline();
    if (Mode.IsEmpty())
    {
        Mode = TEXT("active_component_tick_delta");
    }

    if (!Mode.Equals(TEXT("active_component_tick_delta"), ESearchCase::IgnoreCase)
        && !Mode.Equals(TEXT("live_component_tick_delta"), ESearchCase::IgnoreCase))
    {
        TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Runtime mode '%s' is not implemented yet. Use mode='active_component_tick_delta' or dry_run=true."),
            *Mode));
        ErrorObj->SetStringField(TEXT("requested_mode"), Mode);
        ErrorObj->SetStringField(TEXT("implemented_mode"), TEXT("active_component_tick_delta"));
        ErrorObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
        ErrorObj->SetBoolField(TEXT("same_instance_prepost"), false);
        ErrorObj->SetBoolField(TEXT("original_assets_modified"), false);
        ErrorObj->SetObjectField(TEXT("target_node"), TargetNodeObject);
        AddGraphField(ErrorObj, Blueprint, TargetGraph);
        return ErrorObj;
    }

    bool bPreferPIEWorld = true;
    Params->TryGetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    const bool bRequirePIEWorld = GetBoolParam(Params, TEXT("require_pie_world"), false);
    const bool bAllowMissingSamples = GetBoolParam(Params, TEXT("allow_missing_bones"), false)
        || GetBoolParam(Params, TEXT("allow_missing_samples"), false);
    const int32 SettleTickCount = GetClampedIntParam(Params, TEXT("settle_tick_count"), 0, 0, 240);
    const int32 TickCount = GetClampedIntParam(Params, TEXT("tick_count"), 1, 0, 240);
    const double TickDeltaTime = GetClampedNumberParam(Params, TEXT("tick_delta_time"), 1.0 / 30.0, 0.0, 1.0);
    const bool bRefreshBoneTransforms = GetBoolParam(Params, TEXT("refresh_bone_transforms"), true);

    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;

    if (!bIsolatedSamplerSupported)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(TEXT("Selected node type is not supported by the later isolated sampler MVP; active_component_tick_delta can still sample final component pose deltas.")));
    }

    if (Params->HasField(TEXT("properties")) || Params->HasField(TEXT("property_name")) || Params->HasField(TEXT("curve_values")))
    {
        WarningValues.Add(MakeShared<FJsonValueString>(TEXT("active_component_tick_delta does not apply driver properties or curve values yet; use existing runtime property tools before this call when needed.")));
    }

    FAnimInstanceRuntimeTarget Target;
    FString TargetError;
    if (!FindAnimInstanceRuntimeTarget(Params, bPreferPIEWorld, bRequirePIEWorld, TEXT("sampled"), Target, WarningValues, TargetError))
    {
        TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(TargetError);
        ErrorObj->SetStringField(TEXT("mode"), TEXT("active_component_tick_delta"));
        ErrorObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
        ErrorObj->SetBoolField(TEXT("same_instance_prepost"), false);
        ErrorObj->SetBoolField(TEXT("original_assets_modified"), false);
        ErrorObj->SetObjectField(TEXT("target_node"), TargetNodeObject);
        ErrorObj->SetArrayField(TEXT("warnings"), WarningValues);
        AddGraphField(ErrorObj, Blueprint, TargetGraph);
        return ErrorObj;
    }

    if (Blueprint && Blueprint->GeneratedClass && Target.AnimInstance && !Target.AnimInstance->GetClass()->IsChildOf(Blueprint->GeneratedClass))
    {
        TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Matched AnimInstance class '%s' is not compatible with resolved blueprint '%s'. Pass an actor using this AnimBP."),
            Target.AnimInstance->GetClass() ? *Target.AnimInstance->GetClass()->GetPathName() : TEXT("<none>"),
            *Blueprint->GetPathName()));
        ErrorObj->SetStringField(TEXT("mode"), TEXT("active_component_tick_delta"));
        ErrorObj->SetStringField(TEXT("matched_anim_class"), Target.AnimInstance->GetClass() ? Target.AnimInstance->GetClass()->GetPathName() : FString());
        ErrorObj->SetStringField(TEXT("resolved_blueprint_class"), Blueprint->GeneratedClass->GetPathName());
        ErrorObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
        ErrorObj->SetBoolField(TEXT("same_instance_prepost"), false);
        ErrorObj->SetBoolField(TEXT("original_assets_modified"), false);
        ErrorObj->SetObjectField(TEXT("target_node"), TargetNodeObject);
        AddGraphField(ErrorObj, Blueprint, TargetGraph);
        return ErrorObj;
    }

    TSharedPtr<FJsonObject> SettleTickObject = TickSkeletalComponentForAnimRuntimeProbe(
        Target.Component,
        SettleTickCount,
        TickDeltaTime,
        bRefreshBoneTransforms,
        WarningValues);

    const int32 ErrorCountBeforePreSample = ErrorValues.Num();
    FAnimNodePoseCapture PreTickPose = CaptureAnimNodeProbePose(
        Target.Component,
        SampleBones,
        SampleSockets,
        bAllowMissingSamples,
        ErrorValues,
        WarningValues);
    if (ErrorValues.Num() > ErrorCountBeforePreSample)
    {
        TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("One or more requested sample bones/sockets were missing; pass allow_missing_bones=true to return partial samples."));
        ErrorObj->SetStringField(TEXT("mode"), TEXT("active_component_tick_delta"));
        ErrorObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
        ErrorObj->SetBoolField(TEXT("same_instance_prepost"), false);
        ErrorObj->SetBoolField(TEXT("original_assets_modified"), false);
        ErrorObj->SetObjectField(TEXT("target_node"), TargetNodeObject);
        ErrorObj->SetObjectField(TEXT("settle_tick"), SettleTickObject);
        ErrorObj->SetObjectField(TEXT("pre_tick_pose"), PreTickPose.Json);
        ErrorObj->SetArrayField(TEXT("errors"), ErrorValues);
        ErrorObj->SetArrayField(TEXT("warnings"), WarningValues);
        PopulateAnimInstanceRuntimeTargetFields(ErrorObj, Target, bPreferPIEWorld, bRequirePIEWorld);
        AddGraphField(ErrorObj, Blueprint, TargetGraph);
        return ErrorObj;
    }

    TSharedPtr<FJsonObject> TickObject = TickSkeletalComponentForAnimRuntimeProbe(
        Target.Component,
        TickCount,
        TickDeltaTime,
        bRefreshBoneTransforms,
        WarningValues);

    FAnimNodePoseCapture PostTickPose = CaptureAnimNodeProbePose(
        Target.Component,
        SampleBones,
        SampleSockets,
        bAllowMissingSamples,
        ErrorValues,
        WarningValues);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetBoolField(TEXT("read_only"), false);
    ResultObj->SetBoolField(TEXT("runtime_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetBoolField(TEXT("saves_assets"), false);
    ResultObj->SetBoolField(TEXT("dry_run"), false);
    ResultObj->SetStringField(TEXT("mode"), TEXT("active_component_tick_delta"));
    ResultObj->SetStringField(TEXT("comparison_kind"), TEXT("active_component_tick_delta"));
    ResultObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
    ResultObj->SetBoolField(TEXT("same_instance_prepost"), false);
    ResultObj->SetBoolField(TEXT("original_assets_modified"), false);
    ResultObj->SetBoolField(TEXT("temp_assets_created"), false);
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Samples final SkeletalMeshComponent pose before and after forced ticks on an active component. This is not true internal AnimGraph node source-vs-output instrumentation."));
    ResultObj->SetStringField(TEXT("blueprint_name"), BlueprintName);
    ResultObj->SetStringField(TEXT("blueprint_path"), Blueprint ? Blueprint->GetPathName() : FString());
    ResultObj->SetObjectField(TEXT("target_node"), TargetNodeObject);
    ResultObj->SetArrayField(TEXT("requested_sample_bones"), StringArrayToJsonValues(SampleBones));
    ResultObj->SetArrayField(TEXT("requested_sample_sockets"), StringArrayToJsonValues(SampleSockets));
    ResultObj->SetBoolField(TEXT("allow_missing_bones"), bAllowMissingSamples);
    ResultObj->SetObjectField(TEXT("settle_tick"), SettleTickObject);
    ResultObj->SetObjectField(TEXT("tick"), TickObject);
    ResultObj->SetObjectField(TEXT("pre_tick_pose"), PreTickPose.Json);
    ResultObj->SetObjectField(TEXT("post_tick_pose"), PostTickPose.Json);
    ResultObj->SetObjectField(TEXT("deltas"), BuildAnimNodePoseDeltas(PreTickPose, PostTickPose, SampleBones, SampleSockets));
    PopulateAnimInstanceRuntimeTargetFields(ResultObj, Target, bPreferPIEWorld, bRequirePIEWorld);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

UEdGraphPin* FindPreferredInputPosePinForNode(UEdGraphNode* Node)
{
    if (UEdGraphPin* ComponentPosePin = FindFirstComponentPosePin(Node, EGPD_Input, { TEXT("ComponentPose") }))
    {
        return ComponentPosePin;
    }
    return FindFirstPosePin(Node, EGPD_Input, { TEXT("Pose"), TEXT("Result") });
}

UEdGraphPin* FindPreferredOutputPosePinForNode(UEdGraphNode* Node)
{
    if (UEdGraphPin* ComponentPosePin = FindFirstComponentPosePin(Node, EGPD_Output, { TEXT("Pose"), TEXT("ComponentPose") }))
    {
        return ComponentPosePin;
    }
    return FindFirstPosePin(Node, EGPD_Output, { TEXT("Pose"), TEXT("Result") });
}

FString GetConnectionResponseName(ECanCreateConnectionResponse Response);

bool EnsureAnimGraphConnection(
    UEdGraph* Graph,
    UEdGraphPin* SourcePin,
    UEdGraphPin* TargetPin,
    bool bReplaceExisting,
    bool& bOutChanged,
    FString& OutError,
    TSharedPtr<FJsonObject>* OutErrorObj = nullptr)
{
    bOutChanged = false;
    OutError.Reset();

    if (!Graph || !SourcePin || !TargetPin)
    {
        OutError = TEXT("Invalid graph or pins for AnimGraph connection");
        return false;
    }

    if (TargetPin->LinkedTo.Contains(SourcePin))
    {
        return true;
    }

    if (TargetPin->LinkedTo.Num() > 0)
    {
        if (!bReplaceExisting)
        {
            TArray<TSharedPtr<FJsonValue>> ExistingLinks;
            for (UEdGraphPin* LinkedPin : TargetPin->LinkedTo)
            {
                ExistingLinks.Add(MakeShared<FJsonValueObject>(PinToJson(LinkedPin)));
            }

            OutError = FString::Printf(TEXT("AnimGraph target pose pin already has a different link: %s"), *TargetPin->PinName.ToString());
            if (OutErrorObj)
            {
                TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(OutError);
                ErrorObj->SetObjectField(TEXT("target_pin"), PinToJson(TargetPin));
                ErrorObj->SetArrayField(TEXT("existing_links"), ExistingLinks);
                *OutErrorObj = ErrorObj;
            }
            return false;
        }

        TargetPin->BreakAllPinLinks();
        bOutChanged = true;
    }

    const UEdGraphSchema* GraphSchema = Graph->GetSchema();
    if (!GraphSchema)
    {
        OutError = TEXT("Failed to get AnimationGraph schema");
        return false;
    }

    const FPinConnectionResponse ConnectionResponse = GraphSchema->CanCreateConnection(SourcePin, TargetPin);
    if (!ConnectionResponse.CanSafeConnect() && (!bReplaceExisting || ConnectionResponse.Response == CONNECT_RESPONSE_DISALLOW))
    {
        OutError = ConnectionResponse.Message.ToString();
        if (OutErrorObj)
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(OutError);
            ErrorObj->SetStringField(TEXT("schema_response"), GetConnectionResponseName(ConnectionResponse.Response));
            ErrorObj->SetStringField(TEXT("schema_message"), ConnectionResponse.Message.ToString());
            ErrorObj->SetObjectField(TEXT("source_pin"), PinToJson(SourcePin));
            ErrorObj->SetObjectField(TEXT("target_pin"), PinToJson(TargetPin));
            *OutErrorObj = ErrorObj;
        }
        return false;
    }

    if (!GraphSchema->TryCreateConnection(SourcePin, TargetPin))
    {
        OutError = FString::Printf(TEXT("AnimationGraph schema failed to create connection from %s to %s"), *SourcePin->PinName.ToString(), *TargetPin->PinName.ToString());
        return false;
    }

    bOutChanged = true;
    return true;
}

FString GetConnectionResponseName(ECanCreateConnectionResponse Response)
{
    switch (Response)
    {
    case CONNECT_RESPONSE_MAKE:
        return TEXT("make");
    case CONNECT_RESPONSE_DISALLOW:
        return TEXT("disallow");
    case CONNECT_RESPONSE_BREAK_OTHERS_A:
        return TEXT("break_others_a");
    case CONNECT_RESPONSE_BREAK_OTHERS_B:
        return TEXT("break_others_b");
    case CONNECT_RESPONSE_BREAK_OTHERS_AB:
        return TEXT("break_others_ab");
    case CONNECT_RESPONSE_MAKE_WITH_CONVERSION_NODE:
        return TEXT("make_with_conversion_node");
    case CONNECT_RESPONSE_MAKE_WITH_PROMOTION:
        return TEXT("make_with_promotion");
    default:
        return TEXT("unknown");
    }
}

TSharedPtr<FJsonObject> CreateBlueprintFunctionLibraryNode(
    const TSharedPtr<FJsonObject>& Params,
    UClass* FunctionClass,
    const FName& FunctionName,
    const FString& NodeKind)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!FunctionClass)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Function class not found for %s node"), *NodeKind));
    }

    UFunction* Function = FunctionClass->FindFunctionByName(FunctionName);
    if (!Function)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("%s function not found: %s"), *NodeKind, *FunctionName.ToString()));
    }

    UK2Node_CallFunction* FunctionNode = FUnrealMCPCommonUtils::CreateFunctionCallNode(TargetGraph, Function, NodePosition);
    if (!FunctionNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to create %s node"), *NodeKind));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(FunctionNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}
}

FUnrealMCPBlueprintNodeCommands::FUnrealMCPBlueprintNodeCommands()
{
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("connect_blueprint_nodes"))
    {
        return HandleConnectBlueprintNodes(Params);
    }
    else if (CommandType == TEXT("delete_blueprint_node"))
    {
        return HandleDeleteBlueprintNode(Params);
    }
    else if (CommandType == TEXT("resolve_blueprint"))
    {
        return HandleResolveBlueprint(Params);
    }
    else if (CommandType == TEXT("list_blueprint_nodes"))
    {
        return HandleListBlueprintNodes(Params);
    }
    else if (CommandType == TEXT("inspect_anim_graph_node_settings"))
    {
        return HandleInspectAnimGraphNodeSettings(Params);
    }
    else if (CommandType == TEXT("inspect_anim_state_machine_transitions"))
    {
        return HandleInspectAnimStateMachineTransitions(Params);
    }
    else if (CommandType == TEXT("controlrig_direct_gate_probe"))
    {
        return HandleControlRigDirectGateProbe(Params);
    }
    else if (CommandType == TEXT("sample_controlrig_pre_post_runtime_pose"))
    {
        return HandleSampleControlRigPrePostRuntimePose(Params);
    }
    else if (CommandType == TEXT("sample_anim_node_pre_post_runtime_pose"))
    {
        return HandleSampleAnimNodePrePostRuntimePose(Params);
    }
    else if (CommandType == TEXT("sample_skeletal_bones_in_sie"))
    {
        return HandleSampleSkeletalBonesInSIE(Params);
    }
    else if (CommandType == TEXT("inspect_anim_instance_runtime_state"))
    {
        return HandleInspectAnimInstanceRuntimeState(Params);
    }
    else if (CommandType == TEXT("set_anim_instance_runtime_property_for_probe"))
    {
        return HandleSetAnimInstanceRuntimePropertyForProbe(Params);
    }
    else if (CommandType == TEXT("sample_anim_state_machine_runtime_response"))
    {
        return HandleSampleAnimStateMachineRuntimeResponse(Params);
    }
    else if (CommandType == TEXT("set_anim_graph_rigidbody_settings"))
    {
        return HandleSetAnimGraphRigidBodySettings(Params);
    }
    else if (CommandType == TEXT("list_blueprint_graphs"))
    {
        return HandleListBlueprintGraphs(Params);
    }
    else if (CommandType == TEXT("resolve_blueprint_graph"))
    {
        return HandleResolveBlueprintGraph(Params);
    }
    else if (CommandType == TEXT("ensure_anim_graph_input_pose_passthrough"))
    {
        return HandleEnsureAnimGraphInputPosePassthrough(Params);
    }
    else if (CommandType == TEXT("ensure_anim_graph_modify_bone_demo"))
    {
        return HandleEnsureAnimGraphModifyBoneDemo(Params);
    }
    else if (CommandType == TEXT("ensure_anim_graph_modify_curve_demo"))
    {
        return HandleEnsureAnimGraphModifyCurveDemo(Params);
    }
    else if (CommandType == TEXT("set_anim_graph_controlrig_input_defaults"))
    {
        return HandleSetAnimGraphControlRigInputDefaults(Params);
    }
    else if (CommandType == TEXT("ensure_controlrig_forced_driver_animbp"))
    {
        return HandleEnsureControlRigForcedDriverAnimBP(Params);
    }
    else if (CommandType == TEXT("ensure_anim_graph_trail_demo"))
    {
        return HandleEnsureAnimGraphTrailDemo(Params);
    }
    else if (CommandType == TEXT("add_blueprint_get_self_component_reference"))
    {
        return HandleAddBlueprintGetSelfComponentReference(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_node"))
    {
        return HandleAddBlueprintEvent(Params);
    }
    else if (CommandType == TEXT("add_blueprint_function_node"))
    {
        return HandleAddBlueprintFunctionCall(Params);
    }
    else if (CommandType == TEXT("add_blueprint_call_function_node"))
    {
        return HandleAddBlueprintCallFunctionNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_variable"))
    {
        return HandleAddBlueprintVariable(Params);
    }
    else if (CommandType == TEXT("set_blueprint_variable_metadata"))
    {
        return HandleSetBlueprintVariableMetadata(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_dispatcher"))
    {
        return HandleAddBlueprintEventDispatcher(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_dispatcher_call_node"))
    {
        return HandleAddBlueprintEventDispatcherCallNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_custom_event_node"))
    {
        return HandleAddBlueprintCustomEventNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_dispatcher_bind_node"))
    {
        return HandleAddBlueprintEventDispatcherBindNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_dispatcher_unbind_node"))
    {
        return HandleAddBlueprintEventDispatcherUnbindNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_dispatcher_clear_node"))
    {
        return HandleAddBlueprintEventDispatcherClearNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_event_dispatcher_assign_node"))
    {
        return HandleAddBlueprintEventDispatcherAssignNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_function_parameter"))
    {
        return HandleAddBlueprintFunctionParameter(Params);
    }
    else if (CommandType == TEXT("add_blueprint_local_variable"))
    {
        return HandleAddBlueprintLocalVariable(Params);
    }
    else if (CommandType == TEXT("add_blueprint_branch_node"))
    {
        return HandleAddBlueprintBranchNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_sequence_node"))
    {
        return HandleAddBlueprintSequenceNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_return_node"))
    {
        return HandleAddBlueprintReturnNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_dynamic_cast_node"))
    {
        return HandleAddBlueprintDynamicCastNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_loop_node"))
    {
        return HandleAddBlueprintLoopNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_array_function_node"))
    {
        return HandleAddBlueprintArrayFunctionNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_make_array_node"))
    {
        return HandleAddBlueprintMakeArrayNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_input_action_node"))
    {
        return HandleAddBlueprintInputActionNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_input_axis_event_node"))
    {
        return HandleAddBlueprintInputAxisEventNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_enhanced_input_action_node"))
    {
        return HandleAddBlueprintEnhancedInputActionNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_variable_get_node"))
    {
        return HandleAddBlueprintVariableGetNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_variable_set_node"))
    {
        return HandleAddBlueprintVariableSetNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_math_node"))
    {
        return HandleAddBlueprintMathNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_compare_node"))
    {
        return HandleAddBlueprintCompareNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_boolean_node"))
    {
        return HandleAddBlueprintBooleanNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_select_node"))
    {
        return HandleAddBlueprintSelectNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_literal_node"))
    {
        return HandleAddBlueprintLiteralNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_enum_literal_node"))
    {
        return HandleAddBlueprintEnumLiteralNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_is_valid_node"))
    {
        return HandleAddBlueprintIsValidNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_make_struct_node"))
    {
        return HandleAddBlueprintMakeStructNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_break_struct_node"))
    {
        return HandleAddBlueprintBreakStructNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_switch_int_node"))
    {
        return HandleAddBlueprintSwitchIntNode(Params);
    }
    else if (CommandType == TEXT("add_blueprint_switch_enum_node"))
    {
        return HandleAddBlueprintSwitchEnumNode(Params);
    }
    else if (CommandType == TEXT("set_blueprint_pin_default"))
    {
        return HandleSetBlueprintPinDefault(Params);
    }
    else if (CommandType == TEXT("add_blueprint_self_reference"))
    {
        return HandleAddBlueprintSelfReference(Params);
    }
    else if (CommandType == TEXT("find_blueprint_nodes"))
    {
        return HandleFindBlueprintNodes(Params);
    }

    return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Unknown blueprint node command: %s"), *CommandType));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleDeleteBlueprintNode(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing parameters"));
    }

    if (IsBlueprintNodePlaySessionActive())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Blueprint node deletion is blocked while PIE/SIE is active. End play mode before mutating Blueprint graphs through UnrealMCP."));
    }

    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString NodeId;
    if (!Params->TryGetStringField(TEXT("node_id"), NodeId))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'node_id' parameter"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UEdGraphNode* Node = FindNodeById(TargetGraph, NodeId);
    if (!Node)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Node not found: %s"), *NodeId));
    }

    FString ExpectedNodeName;
    Params->TryGetStringField(TEXT("expected_node_name"), ExpectedNodeName);
    if (!ExpectedNodeName.IsEmpty() && !Node->GetName().Equals(ExpectedNodeName, ESearchCase::IgnoreCase))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(
            FString::Printf(TEXT("Expected node name '%s' but found '%s'"), *ExpectedNodeName, *Node->GetName()));
    }

    FString ExpectedNodeClass;
    Params->TryGetStringField(TEXT("expected_node_class"), ExpectedNodeClass);
    const FString ActualNodeClass = Node->GetClass() ? Node->GetClass()->GetName() : FString();
    if (!ExpectedNodeClass.IsEmpty() &&
        !ActualNodeClass.Equals(ExpectedNodeClass, ESearchCase::IgnoreCase) &&
        !ActualNodeClass.EndsWith(ExpectedNodeClass, ESearchCase::IgnoreCase))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(
            FString::Printf(TEXT("Expected node class '%s' but found '%s'"), *ExpectedNodeClass, *ActualNodeClass));
    }

    FString ExpectedTitleContains;
    Params->TryGetStringField(TEXT("expected_title_contains"), ExpectedTitleContains);
    const FString NodeTitle = Node->GetNodeTitle(ENodeTitleType::FullTitle).ToString();
    if (!ExpectedTitleContains.IsEmpty() && !NodeTitle.Contains(ExpectedTitleContains, ESearchCase::IgnoreCase))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(
            FString::Printf(TEXT("Expected node title containing '%s' but found '%s'"), *ExpectedTitleContains, *NodeTitle));
    }

    if (Node->IsA<UK2Node_Event>() || Node->IsA<UK2Node_FunctionEntry>() || Node->IsA<UK2Node_FunctionResult>())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(
            FString::Printf(TEXT("Refusing to delete structural Blueprint node '%s'. delete_blueprint_node only supports ordinary graph cleanup nodes."), *NodeTitle));
    }

    int32 TotalLinkCount = 0;
    int32 ExecLinkCount = 0;
    int32 NonExecLinkCount = 0;
    TArray<TSharedPtr<FJsonValue>> LinkedPinValues;
    for (UEdGraphPin* Pin : Node->Pins)
    {
        if (!Pin || Pin->LinkedTo.Num() == 0)
        {
            continue;
        }

        const bool bIsExecPin = Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Exec;
        TotalLinkCount += Pin->LinkedTo.Num();
        if (bIsExecPin)
        {
            ExecLinkCount += Pin->LinkedTo.Num();
        }
        else
        {
            NonExecLinkCount += Pin->LinkedTo.Num();
        }

        for (UEdGraphPin* LinkedPin : Pin->LinkedTo)
        {
            TSharedPtr<FJsonObject> LinkObj = MakeShared<FJsonObject>();
            LinkObj->SetStringField(TEXT("pin_name"), Pin->PinName.ToString());
            LinkObj->SetStringField(TEXT("pin_direction"), GetPinDirectionName(Pin));
            LinkObj->SetBoolField(TEXT("is_exec"), bIsExecPin);
            LinkObj->SetStringField(TEXT("linked_node_name"), LinkedPin && LinkedPin->GetOwningNode() ? LinkedPin->GetOwningNode()->GetName() : FString());
            LinkObj->SetStringField(TEXT("linked_node_class"), LinkedPin && LinkedPin->GetOwningNode() && LinkedPin->GetOwningNode()->GetClass() ? LinkedPin->GetOwningNode()->GetClass()->GetName() : FString());
            LinkObj->SetStringField(TEXT("linked_pin_name"), LinkedPin ? LinkedPin->PinName.ToString() : FString());
            LinkedPinValues.Add(MakeShared<FJsonValueObject>(LinkObj));
        }
    }

    const bool bAllowAnyLinkedDelete = GetBoolParam(Params, TEXT("allow_any_linked_delete"), false);
    const bool bAllowExecLinkedDelete = GetBoolParam(Params, TEXT("allow_exec_linked_delete"), false);
    const bool bAllowNonExecLinkedDelete = GetBoolParam(Params, TEXT("allow_non_exec_linked_delete"), false);
    if (ExecLinkCount > 0 && !bAllowAnyLinkedDelete && !bAllowExecLinkedDelete)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(
            FString::Printf(TEXT("Node has %d exec link(s). Pass allow_exec_linked_delete=true to delete it."), ExecLinkCount));
    }
    if (NonExecLinkCount > 0 && !bAllowAnyLinkedDelete && !bAllowNonExecLinkedDelete)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(
            FString::Printf(TEXT("Node has %d non-exec link(s). Pass allow_non_exec_linked_delete=true to delete it."), NonExecLinkCount));
    }

    TSharedPtr<FJsonObject> DeletedNodeJson = NodeToJson(Node, true);
    TargetGraph->Modify();
    Node->Modify();
    Node->BreakAllNodeLinks();
    Node->DestroyNode();
    TargetGraph->NotifyGraphChanged();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("deleted"), true);
    ResultObj->SetStringField(TEXT("node_id"), NodeId);
    ResultObj->SetStringField(TEXT("node_name"), DeletedNodeJson->GetStringField(TEXT("name")));
    ResultObj->SetStringField(TEXT("node_class"), DeletedNodeJson->GetStringField(TEXT("class")));
    ResultObj->SetStringField(TEXT("node_title"), NodeTitle);
    ResultObj->SetNumberField(TEXT("total_link_count"), TotalLinkCount);
    ResultObj->SetNumberField(TEXT("exec_link_count"), ExecLinkCount);
    ResultObj->SetNumberField(TEXT("non_exec_link_count"), NonExecLinkCount);
    ResultObj->SetArrayField(TEXT("broken_links"), LinkedPinValues);
    ResultObj->SetObjectField(TEXT("deleted_node"), DeletedNodeJson);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleConnectBlueprintNodes(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString SourceNodeId;
    if (!Params->TryGetStringField(TEXT("source_node_id"), SourceNodeId))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'source_node_id' parameter"));
    }

    FString TargetNodeId;
    if (!Params->TryGetStringField(TEXT("target_node_id"), TargetNodeId))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'target_node_id' parameter"));
    }

    FString SourcePinName;
    if (!Params->TryGetStringField(TEXT("source_pin"), SourcePinName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'source_pin' parameter"));
    }

    FString TargetPinName;
    if (!Params->TryGetStringField(TEXT("target_pin"), TargetPinName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'target_pin' parameter"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // Find the nodes
    UEdGraphNode* SourceNode = FindNodeById(TargetGraph, SourceNodeId);
    UEdGraphNode* TargetNode = FindNodeById(TargetGraph, TargetNodeId);

    if (!SourceNode || !TargetNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Source or target node not found"));
    }

    UEdGraphPin* SourcePin = FUnrealMCPCommonUtils::FindPin(SourceNode, SourcePinName, EGPD_Output);
    if (!SourcePin)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Source output pin not found: %s"), *SourcePinName));
    }

    UEdGraphPin* TargetPin = FUnrealMCPCommonUtils::FindPin(TargetNode, TargetPinName, EGPD_Input);
    if (!TargetPin)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Target input pin not found: %s"), *TargetPinName));
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    const FPinConnectionResponse ConnectionResponse = K2Schema->CanCreateConnection(SourcePin, TargetPin);

    bool bAllowPinLinkReplacement = false;
    if (Params->HasField(TEXT("allow_pin_link_replacement")))
    {
        bAllowPinLinkReplacement = Params->GetBoolField(TEXT("allow_pin_link_replacement"));
    }

    if (!ConnectionResponse.CanSafeConnect() && (!bAllowPinLinkReplacement || ConnectionResponse.Response == CONNECT_RESPONSE_DISALLOW))
    {
        TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(ConnectionResponse.Message.ToString());
        ErrorObj->SetStringField(TEXT("schema_response"), GetConnectionResponseName(ConnectionResponse.Response));
        ErrorObj->SetStringField(TEXT("schema_message"), ConnectionResponse.Message.ToString());
        ErrorObj->SetObjectField(TEXT("source_pin"), PinToJson(SourcePin));
        ErrorObj->SetObjectField(TEXT("target_pin"), PinToJson(TargetPin));
        return ErrorObj;
    }

    if (!K2Schema->TryCreateConnection(SourcePin, TargetPin))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("K2 schema failed to create connection"));
    }

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("source_node_id"), SourceNodeId);
    ResultObj->SetStringField(TEXT("target_node_id"), TargetNodeId);
    ResultObj->SetStringField(TEXT("source_pin"), SourcePinName);
    ResultObj->SetStringField(TEXT("target_pin"), TargetPinName);
    ResultObj->SetBoolField(TEXT("connected"), true);
    ResultObj->SetStringField(TEXT("schema_response"), GetConnectionResponseName(ConnectionResponse.Response));
    ResultObj->SetStringField(TEXT("schema_message"), ConnectionResponse.Message.ToString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintGetSelfComponentReference(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString ComponentName;
    if (!Params->TryGetStringField(TEXT("component_name"), ComponentName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'component_name' parameter"));
    }

    // Get position parameters (optional)
    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // We'll skip component verification since the GetAllNodes API may have changed in UE5.5

    // Create the variable get node directly
    UK2Node_VariableGet* GetComponentNode = NewObject<UK2Node_VariableGet>(TargetGraph);
    if (!GetComponentNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create get component node"));
    }

    // Set up the variable reference properly for UE5.5
    FMemberReference& VarRef = GetComponentNode->VariableReference;
    VarRef.SetSelfMember(FName(*ComponentName));

    // Set node position
    GetComponentNode->NodePosX = NodePosition.X;
    GetComponentNode->NodePosY = NodePosition.Y;

    // Add to graph
    TargetGraph->AddNode(GetComponentNode);
    GetComponentNode->CreateNewGuid();
    GetComponentNode->PostPlacedNewNode();
    GetComponentNode->AllocateDefaultPins();

    // Explicitly reconstruct node for UE5.5
    GetComponentNode->ReconstructNode();

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("node_id"), GetComponentNode->NodeGuid.ToString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEvent(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString EventName;
    if (!Params->TryGetStringField(TEXT("event_name"), EventName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'event_name' parameter"));
    }

    // Get position parameters (optional)
    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // Create the event node
    UK2Node_Event* EventNode = FUnrealMCPCommonUtils::CreateEventNode(TargetGraph, EventName, NodePosition);
    if (!EventNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create event node"));
    }

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("node_id"), EventNode->NodeGuid.ToString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintFunctionCall(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString FunctionName;
    if (!Params->TryGetStringField(TEXT("function_name"), FunctionName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'function_name' parameter"));
    }

    // Get position parameters (optional)
    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    // Check for target parameter (optional)
    FString Target;
    Params->TryGetStringField(TEXT("target"), Target);

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // Find the function
    UFunction* Function = nullptr;
    UK2Node_CallFunction* FunctionNode = nullptr;

    // Add extensive logging for debugging
    UE_LOG(LogTemp, Display, TEXT("Looking for function '%s' in target '%s'"),
           *FunctionName, Target.IsEmpty() ? TEXT("Blueprint") : *Target);

    // Check if we have a target class specified
    if (!Target.IsEmpty())
    {
        // Try to find the target class
        UClass* TargetClass = nullptr;

        // First try without a prefix
        TargetClass = FindFirstObject<UClass>(*Target);
        UE_LOG(LogTemp, Display, TEXT("Tried to find class '%s': %s"),
               *Target, TargetClass ? TEXT("Found") : TEXT("Not found"));

        // If not found, try with U prefix (common convention for UE classes)
        if (!TargetClass && !Target.StartsWith(TEXT("U")))
        {
            FString TargetWithPrefix = FString(TEXT("U")) + Target;
            TargetClass = FindFirstObject<UClass>(*TargetWithPrefix);
            UE_LOG(LogTemp, Display, TEXT("Tried to find class '%s': %s"),
                   *TargetWithPrefix, TargetClass ? TEXT("Found") : TEXT("Not found"));
        }

        // If still not found, try with common component names
        if (!TargetClass)
        {
            // Try some common component class names
            TArray<FString> PossibleClassNames;
            PossibleClassNames.Add(FString(TEXT("U")) + Target + TEXT("Component"));
            PossibleClassNames.Add(Target + TEXT("Component"));

            for (const FString& ClassName : PossibleClassNames)
            {
                TargetClass = FindFirstObject<UClass>(*ClassName);
                if (TargetClass)
                {
                    UE_LOG(LogTemp, Display, TEXT("Found class using alternative name '%s'"), *ClassName);
                    break;
                }
            }
        }

        // Special case handling for common classes like UGameplayStatics
        if (!TargetClass && Target == TEXT("UGameplayStatics"))
        {
            // For UGameplayStatics, use a direct reference to known class
            TargetClass = FindFirstObject<UClass>(TEXT("UGameplayStatics"));
            if (!TargetClass)
            {
                // Try loading it from its known package
                TargetClass = LoadObject<UClass>(nullptr, TEXT("/Script/Engine.GameplayStatics"));
                UE_LOG(LogTemp, Display, TEXT("Explicitly loading GameplayStatics: %s"),
                       TargetClass ? TEXT("Success") : TEXT("Failed"));
            }
        }

        // If we found a target class, look for the function there
        if (TargetClass)
        {
            UE_LOG(LogTemp, Display, TEXT("Looking for function '%s' in class '%s'"),
                   *FunctionName, *TargetClass->GetName());

            // First try exact name
            Function = TargetClass->FindFunctionByName(*FunctionName);

            // If not found, try class hierarchy
            UClass* CurrentClass = TargetClass;
            while (!Function && CurrentClass)
            {
                UE_LOG(LogTemp, Display, TEXT("Searching in class: %s"), *CurrentClass->GetName());

                // Try exact match
                Function = CurrentClass->FindFunctionByName(*FunctionName);

                // Try case-insensitive match
                if (!Function)
                {
                    for (TFieldIterator<UFunction> FuncIt(CurrentClass); FuncIt; ++FuncIt)
                    {
                        UFunction* AvailableFunc = *FuncIt;
                        UE_LOG(LogTemp, Display, TEXT("  - Available function: %s"), *AvailableFunc->GetName());

                        if (AvailableFunc->GetName().Equals(FunctionName, ESearchCase::IgnoreCase))
                        {
                            UE_LOG(LogTemp, Display, TEXT("  - Found case-insensitive match: %s"), *AvailableFunc->GetName());
                            Function = AvailableFunc;
                            break;
                        }
                    }
                }

                // Move to parent class
                CurrentClass = CurrentClass->GetSuperClass();
            }

            // Special handling for known functions
            if (!Function)
            {
                if (TargetClass->GetName() == TEXT("GameplayStatics") &&
                    (FunctionName == TEXT("GetActorOfClass") || FunctionName.Equals(TEXT("GetActorOfClass"), ESearchCase::IgnoreCase)))
                {
                    UE_LOG(LogTemp, Display, TEXT("Using special case handling for GameplayStatics::GetActorOfClass"));

                    // Create the function node directly
                    FunctionNode = NewObject<UK2Node_CallFunction>(TargetGraph);
                    if (FunctionNode)
                    {
                        // Direct setup for known function
                        FunctionNode->FunctionReference.SetExternalMember(
                            FName(TEXT("GetActorOfClass")),
                            TargetClass
                        );

                        FunctionNode->NodePosX = NodePosition.X;
                        FunctionNode->NodePosY = NodePosition.Y;
                        TargetGraph->AddNode(FunctionNode);
                        FunctionNode->CreateNewGuid();
                        FunctionNode->PostPlacedNewNode();
                        FunctionNode->AllocateDefaultPins();

                        UE_LOG(LogTemp, Display, TEXT("Created GetActorOfClass node directly"));

                        // List all pins
                        for (UEdGraphPin* Pin : FunctionNode->Pins)
                        {
                            UE_LOG(LogTemp, Display, TEXT("  - Pin: %s, Direction: %d, Category: %s"),
                                   *Pin->PinName.ToString(), (int32)Pin->Direction, *Pin->PinType.PinCategory.ToString());
                        }
                    }
                }
            }
        }
    }

    // If we still haven't found the function, try in the blueprint's class
    if (!Function && !FunctionNode)
    {
        UE_LOG(LogTemp, Display, TEXT("Trying to find function in blueprint class"));
        Function = Blueprint->GeneratedClass->FindFunctionByName(*FunctionName);
    }

    // Create the function call node if we found the function
    if (Function && !FunctionNode)
    {
        FunctionNode = FUnrealMCPCommonUtils::CreateFunctionCallNode(TargetGraph, Function, NodePosition);
    }

    if (!FunctionNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Function not found: %s in target %s"), *FunctionName, Target.IsEmpty() ? TEXT("Blueprint") : *Target));
    }

    // Set parameters if provided
    if (Params->HasField(TEXT("params")))
    {
        const TSharedPtr<FJsonObject>* ParamsObj;
        if (Params->TryGetObjectField(TEXT("params"), ParamsObj))
        {
            // Process parameters
            for (const TPair<FString, TSharedPtr<FJsonValue>>& Param : (*ParamsObj)->Values)
            {
                const FString& ParamName = Param.Key;
                const TSharedPtr<FJsonValue>& ParamValue = Param.Value;

                // Find the parameter pin
                UEdGraphPin* ParamPin = FUnrealMCPCommonUtils::FindPin(FunctionNode, ParamName, EGPD_Input);
                if (ParamPin)
                {
                    UE_LOG(LogTemp, Display, TEXT("Found parameter pin '%s' of category '%s'"),
                           *ParamName, *ParamPin->PinType.PinCategory.ToString());
                    UE_LOG(LogTemp, Display, TEXT("  Current default value: '%s'"), *ParamPin->DefaultValue);
                    if (ParamPin->PinType.PinSubCategoryObject.IsValid())
                    {
                        UE_LOG(LogTemp, Display, TEXT("  Pin subcategory: '%s'"),
                               *ParamPin->PinType.PinSubCategoryObject->GetName());
                    }

                    // Set parameter based on type
                    if (ParamValue->Type == EJson::String)
                    {
                        FString StringVal = ParamValue->AsString();
                        UE_LOG(LogTemp, Display, TEXT("  Setting string parameter '%s' to: '%s'"),
                               *ParamName, *StringVal);

                        // Handle class reference parameters (e.g., ActorClass in GetActorOfClass)
                        if (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Class)
                        {
                            // For class references, we require the exact class name with proper prefix
                            // - Actor classes must start with 'A' (e.g., ACameraActor)
                            // - Non-actor classes must start with 'U' (e.g., UObject)
                            const FString& ClassName = StringVal;

                            // TODO: This likely won't work in UE5.5+, so don't rely on it.
                            UClass* Class = FindFirstObject<UClass>(*ClassName);

                            if (!Class)
                            {
                                Class = LoadObject<UClass>(nullptr, *ClassName);
                                UE_LOG(LogUnrealMCP, Display, TEXT("FindObject<UClass> failed. Assuming soft path  path: %s"), *ClassName);
                            }

                            // If not found, try with Engine module path
                            if (!Class)
                            {
                                FString EngineClassName = FString::Printf(TEXT("/Script/Engine.%s"), *ClassName);
                                Class = LoadObject<UClass>(nullptr, *EngineClassName);
                                UE_LOG(LogUnrealMCP, Display, TEXT("Trying Engine module path: %s"), *EngineClassName);
                            }

                            if (!Class)
                            {
                                UE_LOG(LogUnrealMCP, Error, TEXT("Failed to find class '%s'. Make sure to use the exact class name with proper prefix (A for actors, U for non-actors)"), *ClassName);
                                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to find class '%s'"), *ClassName));
                            }

                            const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
                            if (!K2Schema)
                            {
                                UE_LOG(LogUnrealMCP, Error, TEXT("Failed to get K2Schema"));
                                return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2Schema"));
                            }

                            K2Schema->TrySetDefaultObject(*ParamPin, Class);
                            if (ParamPin->DefaultObject != Class)
                            {
                                UE_LOG(LogUnrealMCP, Error, TEXT("Failed to set class reference for pin '%s' to '%s'"), *ParamPin->PinName.ToString(), *ClassName);
                                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to set class reference for pin '%s'"), *ParamPin->PinName.ToString()));
                            }

                            UE_LOG(LogUnrealMCP, Log, TEXT("Successfully set class reference for pin '%s' to '%s'"), *ParamPin->PinName.ToString(), *ClassName);
                            continue;
                        }
                        else if (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Int)
                        {
                            // Ensure we're using an integer value (no decimal)
                            int32 IntValue = FMath::RoundToInt(ParamValue->AsNumber());
                            ParamPin->DefaultValue = FString::FromInt(IntValue);
                            UE_LOG(LogTemp, Display, TEXT("  Set integer parameter '%s' to: %d (string: '%s')"),
                                   *ParamName, IntValue, *ParamPin->DefaultValue);
                        }
                        else if (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Float)
                        {
                            // For other numeric types
                            float FloatValue = ParamValue->AsNumber();
                            ParamPin->DefaultValue = FString::SanitizeFloat(FloatValue);
                            UE_LOG(LogTemp, Display, TEXT("  Set float parameter '%s' to: %f (string: '%s')"),
                                   *ParamName, FloatValue, *ParamPin->DefaultValue);
                        }
                        else if (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Boolean)
                        {
                            bool BoolValue = ParamValue->AsBool();
                            ParamPin->DefaultValue = BoolValue ? TEXT("true") : TEXT("false");
                            UE_LOG(LogTemp, Display, TEXT("  Set boolean parameter '%s' to: %s"),
                                   *ParamName, *ParamPin->DefaultValue);
                        }
                        else if (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct && ParamPin->PinType.PinSubCategoryObject == TBaseStructure<FVector>::Get())
                        {
                            // Handle array parameters - like Vector parameters
                            const TArray<TSharedPtr<FJsonValue>>* ArrayValue;
                            if (ParamValue->TryGetArray(ArrayValue))
                            {
                                // Check if this could be a vector (array of 3 numbers)
                                if (ArrayValue->Num() == 3)
                                {
                                    // Create a proper vector string: (X=0.0,Y=0.0,Z=1000.0)
                                    float X = (*ArrayValue)[0]->AsNumber();
                                    float Y = (*ArrayValue)[1]->AsNumber();
                                    float Z = (*ArrayValue)[2]->AsNumber();

                                    FString VectorString = FString::Printf(TEXT("(X=%f,Y=%f,Z=%f)"), X, Y, Z);
                                    ParamPin->DefaultValue = VectorString;

                                    UE_LOG(LogTemp, Display, TEXT("  Set vector parameter '%s' to: %s"),
                                           *ParamName, *VectorString);
                                    UE_LOG(LogTemp, Display, TEXT("  Final pin value: '%s'"),
                                           *ParamPin->DefaultValue);
                                }
                                else
                                {
                                    UE_LOG(LogTemp, Warning, TEXT("Array parameter type not fully supported yet"));
                                }
                            }
                        }
                    }
                    else if (ParamValue->Type == EJson::Number)
                    {
                        // Handle integer vs float parameters correctly
                        if (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Int)
                        {
                            // Ensure we're using an integer value (no decimal)
                            int32 IntValue = FMath::RoundToInt(ParamValue->AsNumber());
                            ParamPin->DefaultValue = FString::FromInt(IntValue);
                            UE_LOG(LogTemp, Display, TEXT("  Set integer parameter '%s' to: %d (string: '%s')"),
                                   *ParamName, IntValue, *ParamPin->DefaultValue);
                        }
                        else
                        {
                            // For other numeric types
                            float FloatValue = ParamValue->AsNumber();
                            ParamPin->DefaultValue = FString::SanitizeFloat(FloatValue);
                            UE_LOG(LogTemp, Display, TEXT("  Set float parameter '%s' to: %f (string: '%s')"),
                                   *ParamName, FloatValue, *ParamPin->DefaultValue);
                        }
                    }
                    else if (ParamValue->Type == EJson::Boolean)
                    {
                        bool BoolValue = ParamValue->AsBool();
                        ParamPin->DefaultValue = BoolValue ? TEXT("true") : TEXT("false");
                        UE_LOG(LogTemp, Display, TEXT("  Set boolean parameter '%s' to: %s"),
                               *ParamName, *ParamPin->DefaultValue);
                    }
                    else if (ParamValue->Type == EJson::Array)
                    {
                        UE_LOG(LogTemp, Display, TEXT("  Processing array parameter '%s'"), *ParamName);
                        // Handle array parameters - like Vector parameters
                        const TArray<TSharedPtr<FJsonValue>>* ArrayValue;
                        if (ParamValue->TryGetArray(ArrayValue))
                        {
                            // Check if this could be a vector (array of 3 numbers)
                            if (ArrayValue->Num() == 3 &&
                                (ParamPin->PinType.PinCategory == UEdGraphSchema_K2::PC_Struct) &&
                                (ParamPin->PinType.PinSubCategoryObject == TBaseStructure<FVector>::Get()))
                            {
                                // Create a proper vector string: (X=0.0,Y=0.0,Z=1000.0)
                                float X = (*ArrayValue)[0]->AsNumber();
                                float Y = (*ArrayValue)[1]->AsNumber();
                                float Z = (*ArrayValue)[2]->AsNumber();

                                FString VectorString = FString::Printf(TEXT("(X=%f,Y=%f,Z=%f)"), X, Y, Z);
                                ParamPin->DefaultValue = VectorString;

                                UE_LOG(LogTemp, Display, TEXT("  Set vector parameter '%s' to: %s"),
                                       *ParamName, *VectorString);
                                UE_LOG(LogTemp, Display, TEXT("  Final pin value: '%s'"),
                                       *ParamPin->DefaultValue);
                            }
                            else
                            {
                                UE_LOG(LogTemp, Warning, TEXT("Array parameter type not fully supported yet"));
                            }
                        }
                    }
                    // Add handling for other types as needed
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("Parameter pin '%s' not found"), *ParamName);
                }
            }
        }
    }

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("node_id"), FunctionNode->NodeGuid.ToString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintCallFunctionNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString FunctionName;
    if (!Params->TryGetStringField(TEXT("function_name"), FunctionName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'function_name' parameter"));
    }

    FString FunctionClassName;
    if (!Params->TryGetStringField(TEXT("function_class"), FunctionClassName) &&
        !Params->TryGetStringField(TEXT("class_name"), FunctionClassName) &&
        !Params->TryGetStringField(TEXT("target_class"), FunctionClassName) &&
        !Params->TryGetStringField(TEXT("target"), FunctionClassName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'function_class' parameter"));
    }

    UClass* FunctionClass = LoadClassForPin(FunctionClassName);
    if (!FunctionClass)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Function class not found: %s"), *FunctionClassName));
    }

    FString FunctionError;
    UFunction* Function = ResolveFunctionByName(FunctionClass, FunctionName, FunctionError);
    if (!Function)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FunctionError);
    }

    const bool bAllowLatent = GetBoolParam(Params, TEXT("allow_latent"), false);
    const bool bAllowEditorOnly = GetBoolParam(Params, TEXT("allow_editor_only"), false);
    const bool bAllowWildcard = GetBoolParam(Params, TEXT("allow_wildcard"), false);
    const bool bAllowDeprecated = GetBoolParam(Params, TEXT("allow_deprecated"), false);
    const bool bAllowInternal = GetBoolParam(Params, TEXT("allow_internal"), false);
    FString ValidationError;
    if (!ValidateBlueprintCallableFunction(Function, bAllowLatent, bAllowEditorOnly, bAllowWildcard, bAllowDeprecated, bAllowInternal, ValidationError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(ValidationError);
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    UK2Node_CallFunction* FunctionNode = FUnrealMCPCommonUtils::CreateFunctionCallNode(TargetGraph, Function, NodePosition);
    if (!FunctionNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to create function call node: %s"), *Function->GetPathName()));
    }

    TSharedPtr<FJsonObject> AppliedDefaults = MakeShared<FJsonObject>();
    const TSharedPtr<FJsonObject>* ParamDefaultsObj = nullptr;
    bool bHasParamDefaults = Params->TryGetObjectField(TEXT("param_defaults"), ParamDefaultsObj);
    if (!bHasParamDefaults)
    {
        bHasParamDefaults = Params->TryGetObjectField(TEXT("params"), ParamDefaultsObj);
    }

    if (bHasParamDefaults && ParamDefaultsObj && ParamDefaultsObj->IsValid())
    {
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Param : (*ParamDefaultsObj)->Values)
        {
            UEdGraphPin* ParamPin = FUnrealMCPCommonUtils::FindPin(FunctionNode, Param.Key, EGPD_Input);
            if (!ParamPin)
            {
                FunctionNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Function parameter pin not found: %s"), *Param.Key));
            }

            FString AppliedValue;
            FString DefaultError;
            if (!ApplyPinDefaultValueChecked(ParamPin, Param.Value, K2Schema, AppliedValue, DefaultError))
            {
                FunctionNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for function parameter '%s': %s"), *Param.Key, *DefaultError));
            }

            FunctionNode->PinDefaultValueChanged(ParamPin);
            AppliedDefaults->SetStringField(Param.Key, AppliedValue);
        }
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(FunctionNode, true);
    ResultObj->SetStringField(TEXT("function_name"), Function->GetName());
    ResultObj->SetStringField(TEXT("function_class"), Function->GetOuterUClass() ? Function->GetOuterUClass()->GetPathName() : FunctionClass->GetPathName());
    ResultObj->SetBoolField(TEXT("is_static"), Function->HasAnyFunctionFlags(FUNC_Static));
    ResultObj->SetBoolField(TEXT("is_pure"), Function->HasAnyFunctionFlags(FUNC_BlueprintPure));
    ResultObj->SetBoolField(TEXT("is_latent"), Function->HasMetaData(FBlueprintMetadata::MD_Latent));
    ResultObj->SetObjectField(TEXT("param_defaults_applied"), AppliedDefaults);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintVariable(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString VariableName;
    if (!Params->TryGetStringField(TEXT("variable_name"), VariableName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_name' parameter"));
    }

    FString VariableType;
    if (!Params->TryGetStringField(TEXT("variable_type"), VariableType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_type' parameter"));
    }

    // Get optional parameters
    bool IsExposed = false;
    if (Params->HasField(TEXT("is_exposed")))
    {
        IsExposed = Params->GetBoolField(TEXT("is_exposed"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FEdGraphPinType PinType;
    FString TypeError;
    if (!BuildPinTypeFromDescriptor(VariableType, Params, TEXT("type_object"), PinType, TypeError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TypeError);
    }

    FString DefaultValue;
    if (const TSharedPtr<FJsonValue> DefaultJsonValue = Params->TryGetField(TEXT("default_value")))
    {
        FString DefaultError;
        if (!GetPinDefaultStringForTypeChecked(DefaultJsonValue, PinType, DefaultValue, DefaultError))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for variable '%s': %s"), *VariableName, *DefaultError));
        }
    }

    if (!FBlueprintEditorUtils::AddMemberVariable(Blueprint, FName(*VariableName), PinType, DefaultValue))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to add member variable: %s"), *VariableName));
    }

    // Set variable properties
    FBPVariableDescription* NewVar = nullptr;
    for (FBPVariableDescription& Variable : Blueprint->NewVariables)
    {
        if (Variable.VarName == FName(*VariableName))
        {
            NewVar = &Variable;
            break;
        }
    }

    if (NewVar)
    {
        if (Params->HasField(TEXT("category")))
        {
            const FString Category = GetStringParam(Params, TEXT("category"));
            NewVar->Category = FText::FromString(Category);
            FBlueprintEditorUtils::SetBlueprintVariableCategory(Blueprint, FName(*VariableName), nullptr, NewVar->Category, true);
        }
        if (Params->HasField(TEXT("tooltip")))
        {
            const FString Tooltip = GetStringParam(Params, TEXT("tooltip"));
            NewVar->SetMetaData(TEXT("Tooltip"), Tooltip);
            FBlueprintEditorUtils::SetBlueprintVariableMetaData(Blueprint, FName(*VariableName), nullptr, TEXT("Tooltip"), Tooltip);
        }
        if (Params->HasField(TEXT("friendly_name")))
        {
            NewVar->FriendlyName = GetStringParam(Params, TEXT("friendly_name"));
        }
        const TSharedPtr<FJsonObject>* MetadataObject = nullptr;
        if (Params->TryGetObjectField(TEXT("metadata"), MetadataObject) && MetadataObject && MetadataObject->IsValid())
        {
            for (const TPair<FString, TSharedPtr<FJsonValue>>& MetadataPair : (*MetadataObject)->Values)
            {
                FString MetadataValue;
                if (MetadataPair.Value->Type == EJson::String)
                {
                    MetadataValue = MetadataPair.Value->AsString();
                }
                else if (MetadataPair.Value->Type == EJson::Boolean)
                {
                    MetadataValue = MetadataPair.Value->AsBool() ? TEXT("true") : TEXT("false");
                }
                else if (MetadataPair.Value->Type == EJson::Number)
                {
                    MetadataValue = FString::SanitizeFloat(MetadataPair.Value->AsNumber());
                }
                else
                {
                    continue;
                }
                NewVar->SetMetaData(FName(*MetadataPair.Key), MetadataValue);
                FBlueprintEditorUtils::SetBlueprintVariableMetaData(Blueprint, FName(*VariableName), nullptr, FName(*MetadataPair.Key), MetadataValue);
            }
        }

        if (IsExposed || GetBoolParam(Params, TEXT("is_editable"), false))
        {
            NewVar->PropertyFlags |= CPF_Edit;
        }
    }

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("variable_name"), VariableName);
    ResultObj->SetStringField(TEXT("variable_type"), VariableType);
    ResultObj->SetStringField(TEXT("default_value"), DefaultValue);
    ResultObj->SetObjectField(TEXT("pin_type"), PinTypeToJson(PinType));
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSetBlueprintVariableMetadata(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString VariableName;
    if (!Params->TryGetStringField(TEXT("variable_name"), VariableName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_name' parameter"));
    }

    const TSharedPtr<FJsonObject>* MetadataObject = nullptr;
    const bool bHasMetadata = Params->TryGetObjectField(TEXT("metadata"), MetadataObject) && MetadataObject && MetadataObject->IsValid();
    const bool bHasFlagEdit =
        Params->HasField(TEXT("is_editable")) ||
        Params->HasField(TEXT("is_exposed")) ||
        Params->HasField(TEXT("instance_editable")) ||
        Params->HasField(TEXT("is_instance_editable")) ||
        Params->HasField(TEXT("expose_on_spawn"));
    if (!bHasMetadata && !bHasFlagEdit)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'metadata' object or variable flag fields"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FBPVariableDescription* TargetVariable = nullptr;
    const FName TargetVariableName(*VariableName);
    for (FBPVariableDescription& Variable : Blueprint->NewVariables)
    {
        if (Variable.VarName == TargetVariableName)
        {
            TargetVariable = &Variable;
            break;
        }
    }
    if (!TargetVariable)
    {
        for (FBPVariableDescription& Variable : Blueprint->GeneratedVariables)
        {
            if (Variable.VarName == TargetVariableName)
            {
                TargetVariable = &Variable;
                break;
            }
        }
    }
    if (!TargetVariable)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint variable not found: %s"), *VariableName));
    }

    TSharedPtr<FJsonObject> AppliedMetadata = MakeShared<FJsonObject>();
    if (bHasMetadata)
    {
        for (const TPair<FString, TSharedPtr<FJsonValue>>& MetadataPair : (*MetadataObject)->Values)
        {
            FString MetadataValue;
            if (MetadataPair.Value->Type == EJson::String)
            {
                MetadataValue = MetadataPair.Value->AsString();
            }
            else if (MetadataPair.Value->Type == EJson::Boolean)
            {
                MetadataValue = MetadataPair.Value->AsBool() ? TEXT("true") : TEXT("false");
            }
            else if (MetadataPair.Value->Type == EJson::Number)
            {
                MetadataValue = FString::SanitizeFloat(MetadataPair.Value->AsNumber());
            }
            else
            {
                continue;
            }

            const FName MetadataKey(*MetadataPair.Key);
            TargetVariable->SetMetaData(MetadataKey, MetadataValue);
            FBlueprintEditorUtils::SetBlueprintVariableMetaData(Blueprint, TargetVariableName, nullptr, MetadataKey, MetadataValue);
            AppliedMetadata->SetStringField(MetadataPair.Key, MetadataValue);
        }
    }

    TSharedPtr<FJsonObject> AppliedFlags = MakeShared<FJsonObject>();
    uint64* PropertyFlags = FBlueprintEditorUtils::GetBlueprintVariablePropertyFlags(Blueprint, TargetVariableName);
    if (!PropertyFlags)
    {
        PropertyFlags = &TargetVariable->PropertyFlags;
    }

    auto ApplyInstanceEditable = [&](bool bEnable)
    {
        if (bEnable)
        {
            *PropertyFlags |= static_cast<uint64>(CPF_Edit);
            *PropertyFlags &= ~static_cast<uint64>(CPF_DisableEditOnInstance);
        }
        else
        {
            *PropertyFlags |= static_cast<uint64>(CPF_DisableEditOnInstance);
        }
        TargetVariable->PropertyFlags = *PropertyFlags;
        AppliedFlags->SetBoolField(TEXT("instance_editable"), bEnable);
    };

    if (Params->HasField(TEXT("is_editable")))
    {
        ApplyInstanceEditable(Params->GetBoolField(TEXT("is_editable")));
        AppliedFlags->SetBoolField(TEXT("is_editable"), Params->GetBoolField(TEXT("is_editable")));
    }
    if (Params->HasField(TEXT("is_exposed")))
    {
        ApplyInstanceEditable(Params->GetBoolField(TEXT("is_exposed")));
        AppliedFlags->SetBoolField(TEXT("is_exposed"), Params->GetBoolField(TEXT("is_exposed")));
    }
    if (Params->HasField(TEXT("instance_editable")))
    {
        ApplyInstanceEditable(Params->GetBoolField(TEXT("instance_editable")));
    }
    if (Params->HasField(TEXT("is_instance_editable")))
    {
        ApplyInstanceEditable(Params->GetBoolField(TEXT("is_instance_editable")));
        AppliedFlags->SetBoolField(TEXT("is_instance_editable"), Params->GetBoolField(TEXT("is_instance_editable")));
    }
    if (Params->HasField(TEXT("expose_on_spawn")))
    {
        const bool bExposeOnSpawn = Params->GetBoolField(TEXT("expose_on_spawn"));
        if (bExposeOnSpawn)
        {
            *PropertyFlags |= static_cast<uint64>(CPF_ExposeOnSpawn);
            FBlueprintEditorUtils::SetBlueprintVariableMetaData(Blueprint, TargetVariableName, nullptr, TEXT("ExposeOnSpawn"), TEXT("true"));
        }
        else
        {
            *PropertyFlags &= ~static_cast<uint64>(CPF_ExposeOnSpawn);
            FBlueprintEditorUtils::RemoveBlueprintVariableMetaData(Blueprint, TargetVariableName, nullptr, TEXT("ExposeOnSpawn"));
        }
        TargetVariable->PropertyFlags = *PropertyFlags;
        AppliedFlags->SetBoolField(TEXT("expose_on_spawn"), bExposeOnSpawn);
    }

    if (AppliedMetadata->Values.IsEmpty() && AppliedFlags->Values.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("No supported metadata or flag values were provided"));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> VerifiedMetadata = MakeShared<FJsonObject>();
    for (const TPair<FString, TSharedPtr<FJsonValue>>& MetadataPair : AppliedMetadata->Values)
    {
        FString VerifiedValue;
        if (FBlueprintEditorUtils::GetBlueprintVariableMetaData(Blueprint, TargetVariableName, nullptr, FName(*MetadataPair.Key), VerifiedValue))
        {
            VerifiedMetadata->SetStringField(MetadataPair.Key, VerifiedValue);
        }
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("blueprint_name"), BlueprintName);
    ResultObj->SetStringField(TEXT("variable_name"), VariableName);
    ResultObj->SetObjectField(TEXT("metadata"), AppliedMetadata);
    ResultObj->SetObjectField(TEXT("verified_metadata"), VerifiedMetadata);
    ResultObj->SetObjectField(TEXT("flags"), AppliedFlags);
    ResultObj->SetNumberField(TEXT("property_flags"), static_cast<double>(*PropertyFlags));
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEventDispatcher(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString DispatcherName;
    if (!Params->TryGetStringField(TEXT("dispatcher_name"), DispatcherName) &&
        !Params->TryGetStringField(TEXT("event_dispatcher_name"), DispatcherName) &&
        !Params->TryGetStringField(TEXT("delegate_name"), DispatcherName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'dispatcher_name' parameter"));
    }

    DispatcherName.TrimStartAndEndInline();
    if (DispatcherName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'dispatcher_name' cannot be empty"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    const FName DispatcherFName(*DispatcherName);
    if (DispatcherFName.IsNone())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'dispatcher_name' must resolve to a valid FName"));
    }

    if (FBlueprintEditorUtils::FindNewVariableIndex(Blueprint, DispatcherFName) != INDEX_NONE)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher already exists: %s"), *DispatcherName));
    }
    if (FindBlueprintGraph(Blueprint, FString(), DispatcherName, TEXT("any")))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint graph already exists with dispatcher name: %s"), *DispatcherName));
    }

    const UEdGraphSchema_K2* K2Schema = GetDefault<UEdGraphSchema_K2>();
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("K2 schema is unavailable"));
    }

    FEdGraphPinType DelegateType;
    DelegateType.PinCategory = UEdGraphSchema_K2::PC_MCDelegate;
    if (!FBlueprintEditorUtils::AddMemberVariable(Blueprint, DispatcherFName, DelegateType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to add event dispatcher variable: %s"), *DispatcherName));
    }

    UEdGraph* NewGraph = FBlueprintEditorUtils::CreateNewGraph(Blueprint, DispatcherFName, UEdGraph::StaticClass(), UEdGraphSchema_K2::StaticClass());
    auto RollbackDispatcher = [&]()
    {
        if (NewGraph)
        {
            FBlueprintEditorUtils::RemoveGraph(Blueprint, NewGraph);
            NewGraph = nullptr;
        }
        FBlueprintEditorUtils::RemoveMemberVariable(Blueprint, DispatcherFName);
    };

    if (!NewGraph)
    {
        RollbackDispatcher();
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to create event dispatcher signature graph: %s"), *DispatcherName));
    }

    NewGraph->bEditable = false;
    K2Schema->CreateDefaultNodesForGraph(*NewGraph);
    K2Schema->CreateFunctionGraphTerminators(*NewGraph, (UClass*)nullptr);
    K2Schema->AddExtraFunctionFlags(NewGraph, FUNC_BlueprintCallable | FUNC_BlueprintEvent | FUNC_Public);
    K2Schema->MarkFunctionEntryAsEditable(NewGraph, true);
    Blueprint->DelegateSignatureGraphs.Add(NewGraph);

    UK2Node_FunctionEntry* EntryNode = Cast<UK2Node_FunctionEntry>(FBlueprintEditorUtils::GetEntryNode(NewGraph));
    if (!EntryNode)
    {
        RollbackDispatcher();
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Event dispatcher signature entry node not found"));
    }

    TArray<TSharedPtr<FJsonValue>> InputValues;
    const TArray<TSharedPtr<FJsonValue>>* InputValuesPtr = nullptr;
    if (Params->TryGetArrayField(TEXT("inputs"), InputValuesPtr) && InputValuesPtr)
    {
        InputValues = *InputValuesPtr;
    }
    else if (Params->TryGetArrayField(TEXT("parameters"), InputValuesPtr) && InputValuesPtr)
    {
        InputValues = *InputValuesPtr;
    }

    TArray<TSharedPtr<FJsonValue>> CreatedInputs;
    for (int32 InputIndex = 0; InputIndex < InputValues.Num(); ++InputIndex)
    {
        const TSharedPtr<FJsonObject>* InputObject = nullptr;
        if (!InputValues[InputIndex].IsValid() || !InputValues[InputIndex]->TryGetObject(InputObject) || !InputObject || !InputObject->IsValid())
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher input %d must be an object"), InputIndex));
        }

        FString ParameterName;
        if (!(*InputObject)->TryGetStringField(TEXT("parameter_name"), ParameterName) &&
            !(*InputObject)->TryGetStringField(TEXT("name"), ParameterName))
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Missing input name for event dispatcher input %d"), InputIndex));
        }
        ParameterName.TrimStartAndEndInline();
        if (ParameterName.IsEmpty())
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher input %d name cannot be empty"), InputIndex));
        }

        FString ParameterType;
        if (!(*InputObject)->TryGetStringField(TEXT("parameter_type"), ParameterType) &&
            !(*InputObject)->TryGetStringField(TEXT("type"), ParameterType))
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Missing input type for event dispatcher input '%s'"), *ParameterName));
        }

        FEdGraphPinType PinType;
        FString TypeError;
        if (!BuildPinTypeFromDescriptor(ParameterType, *InputObject, TEXT("type_object"), PinType, TypeError))
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid input type for event dispatcher input '%s': %s"), *ParameterName, *TypeError));
        }

        const FName ParameterFName(*ParameterName);
        if (ParameterFName.IsNone())
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid input name for event dispatcher input %d"), InputIndex));
        }
        if (FUnrealMCPCommonUtils::FindPin(EntryNode, ParameterName, EGPD_Output))
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher input already exists: %s"), *ParameterName));
        }

        FText PinError;
        if (!EntryNode->CanCreateUserDefinedPin(PinType, EGPD_Output, PinError))
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(PinError.ToString());
        }

        UEdGraphPin* NewPin = EntryNode->CreateUserDefinedPin(ParameterFName, PinType, EGPD_Output, false);
        if (!NewPin)
        {
            RollbackDispatcher();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to add event dispatcher input: %s"), *ParameterName));
        }

        TSharedPtr<FJsonObject> CreatedInput = MakeShared<FJsonObject>();
        CreatedInput->SetStringField(TEXT("parameter_name"), ParameterName);
        CreatedInput->SetStringField(TEXT("parameter_type"), ParameterType);
        CreatedInput->SetObjectField(TEXT("pin_type"), PinTypeToJson(PinType));
        CreatedInputs.Add(MakeShared<FJsonValueObject>(CreatedInput));
    }

    if (CreatedInputs.Num() > 0)
    {
        EntryNode->ReconstructNode();
    }

    FBPVariableDescription* DispatcherVariable = nullptr;
    for (FBPVariableDescription& Variable : Blueprint->NewVariables)
    {
        if (Variable.VarName == DispatcherFName)
        {
            DispatcherVariable = &Variable;
            break;
        }
    }

    if (DispatcherVariable)
    {
        if (Params->HasField(TEXT("category")))
        {
            const FString Category = GetStringParam(Params, TEXT("category"));
            DispatcherVariable->Category = FText::FromString(Category);
            FBlueprintEditorUtils::SetBlueprintVariableCategory(Blueprint, DispatcherFName, nullptr, DispatcherVariable->Category, true);
        }
        if (Params->HasField(TEXT("tooltip")))
        {
            const FString Tooltip = GetStringParam(Params, TEXT("tooltip"));
            DispatcherVariable->SetMetaData(TEXT("Tooltip"), Tooltip);
            FBlueprintEditorUtils::SetBlueprintVariableMetaData(Blueprint, DispatcherFName, nullptr, TEXT("Tooltip"), Tooltip);
        }
        if (Params->HasField(TEXT("friendly_name")))
        {
            DispatcherVariable->FriendlyName = GetStringParam(Params, TEXT("friendly_name"));
        }
    }

    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("dispatcher_name"), DispatcherName);
    ResultObj->SetObjectField(TEXT("pin_type"), PinTypeToJson(DelegateType));
    ResultObj->SetObjectField(TEXT("signature_graph"), GraphToJson(Blueprint, NewGraph));
    ResultObj->SetArrayField(TEXT("inputs"), CreatedInputs);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEventDispatcherCallNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString DispatcherName;
    if (!Params->TryGetStringField(TEXT("dispatcher_name"), DispatcherName) &&
        !Params->TryGetStringField(TEXT("event_dispatcher_name"), DispatcherName) &&
        !Params->TryGetStringField(TEXT("delegate_name"), DispatcherName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'dispatcher_name' parameter"));
    }

    DispatcherName.TrimStartAndEndInline();
    if (DispatcherName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'dispatcher_name' cannot be empty"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    FMulticastDelegateProperty* DelegateProperty = FindBlueprintMulticastDelegateProperty(Blueprint, FName(*DispatcherName));
    if (!DelegateProperty)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher property not found: %s. Compile or recreate the dispatcher before adding a call node."), *DispatcherName));
    }
    if (!DelegateProperty->HasAllPropertyFlags(CPF_BlueprintCallable))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher is not BlueprintCallable: %s"), *DispatcherName));
    }
    if (!DelegateProperty->SignatureFunction)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher signature is not available: %s"), *DispatcherName));
    }

    UK2Node_CallDelegate* CallNode = NewObject<UK2Node_CallDelegate>(TargetGraph);
    if (!CallNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create Event Dispatcher call node"));
    }

    const bool bSelfContext = IsSelfContextForDelegateProperty(Blueprint, DelegateProperty);
    CallNode->SetFromProperty(DelegateProperty, bSelfContext, DelegateProperty->GetOwnerClass());
    if (!CallNode->IsCompatibleWithGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Event Dispatcher call nodes are only supported in event or function graphs"));
    }

    CallNode->NodePosX = NodePosition.X;
    CallNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(CallNode, true);
    CallNode->CreateNewGuid();
    CallNode->PostPlacedNewNode();
    CallNode->AllocateDefaultPins();
    CallNode->ReconstructNode();

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(CallNode, true);
    ResultObj->SetStringField(TEXT("dispatcher_name"), DispatcherName);
    ResultObj->SetStringField(TEXT("signature_function"), DelegateProperty->SignatureFunction->GetPathName());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintCustomEventNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString CustomEventName;
    if (!Params->TryGetStringField(TEXT("custom_event_name"), CustomEventName) &&
        !Params->TryGetStringField(TEXT("event_name"), CustomEventName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'custom_event_name' parameter"));
    }

    CustomEventName.TrimStartAndEndInline();
    if (CustomEventName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'custom_event_name' cannot be empty"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (GetBlueprintGraphType(Blueprint, TargetGraph) != TEXT("event"))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Custom event nodes are only supported in event graphs"));
    }

    const FName CustomEventFName(*CustomEventName);
    TArray<UK2Node_CustomEvent*> ExistingCustomEvents;
    FBlueprintEditorUtils::GetAllNodesOfClass<UK2Node_CustomEvent>(Blueprint, ExistingCustomEvents);
    for (UK2Node_CustomEvent* ExistingCustomEvent : ExistingCustomEvents)
    {
        if (ExistingCustomEvent && ExistingCustomEvent->CustomFunctionName == CustomEventFName)
        {
            // Reuse the existing custom event node; apply call_in_editor update if requested.
            bool bExistingCallInEditor = false;
            if (Params->TryGetBoolField(TEXT("call_in_editor"), bExistingCallInEditor))
            {
                ExistingCustomEvent->Modify();
                ExistingCustomEvent->bCallInEditor = bExistingCallInEditor;
                ExistingCustomEvent->ReconstructNode();
                FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
            }
            TSharedPtr<FJsonObject> ExistingResultObj = NodeToJson(ExistingCustomEvent, true);
            ExistingResultObj->SetStringField(TEXT("custom_event_name"), CustomEventName);
            ExistingResultObj->SetBoolField(TEXT("reused_existing"), true);
            ExistingResultObj->SetBoolField(TEXT("call_in_editor"), ExistingCustomEvent->bCallInEditor);
            AddGraphField(ExistingResultObj, Blueprint, ExistingCustomEvent->GetGraph());
            return ExistingResultObj;
        }
    }

    FString SignatureSourceDispatcherName;
    Params->TryGetStringField(TEXT("signature_source_dispatcher_name"), SignatureSourceDispatcherName);
    SignatureSourceDispatcherName.TrimStartAndEndInline();

    const UFunction* SignatureFunction = nullptr;
    if (!SignatureSourceDispatcherName.IsEmpty())
    {
        FMulticastDelegateProperty* DelegateProperty = FindBlueprintMulticastDelegateProperty(Blueprint, FName(*SignatureSourceDispatcherName));
        if (!DelegateProperty)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Signature source Event Dispatcher property not found: %s"), *SignatureSourceDispatcherName));
        }
        SignatureFunction = DelegateProperty->SignatureFunction;
        if (!SignatureFunction)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Signature source Event Dispatcher signature is not available: %s"), *SignatureSourceDispatcherName));
        }
    }

    UK2Node_CustomEvent* CustomEventNode = nullptr;
    if (SignatureFunction)
    {
        CustomEventNode = UK2Node_CustomEvent::CreateFromFunction(NodePosition, TargetGraph, CustomEventName, SignatureFunction, false);
    }
    else
    {
        CustomEventNode = NewObject<UK2Node_CustomEvent>(TargetGraph);
        if (CustomEventNode)
        {
            CustomEventNode->CustomFunctionName = CustomEventFName;
            CustomEventNode->SetFlags(RF_Transactional);
            CustomEventNode->NodePosX = NodePosition.X;
            CustomEventNode->NodePosY = NodePosition.Y;
            TargetGraph->Modify();
            TargetGraph->AddNode(CustomEventNode, true, false);
            CustomEventNode->CreateNewGuid();
            CustomEventNode->PostPlacedNewNode();
            CustomEventNode->AllocateDefaultPins();
        }
    }

    if (!CustomEventNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to create custom event node: %s"), *CustomEventName));
    }

    bool bCallInEditor = false;
    if (Params->TryGetBoolField(TEXT("call_in_editor"), bCallInEditor) && bCallInEditor)
    {
        CustomEventNode->bCallInEditor = true;
    }

    CustomEventNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(CustomEventNode, true);
    ResultObj->SetStringField(TEXT("custom_event_name"), CustomEventName);
    ResultObj->SetStringField(TEXT("signature_source_dispatcher_name"), SignatureSourceDispatcherName);
    ResultObj->SetStringField(TEXT("signature_function"), SignatureFunction ? SignatureFunction->GetPathName() : FString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEventDispatcherBindNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString DispatcherName;
    if (!Params->TryGetStringField(TEXT("dispatcher_name"), DispatcherName) &&
        !Params->TryGetStringField(TEXT("event_dispatcher_name"), DispatcherName) &&
        !Params->TryGetStringField(TEXT("delegate_name"), DispatcherName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'dispatcher_name' parameter"));
    }

    DispatcherName.TrimStartAndEndInline();
    if (DispatcherName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'dispatcher_name' cannot be empty"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    FMulticastDelegateProperty* DelegateProperty = FindBlueprintMulticastDelegateProperty(Blueprint, FName(*DispatcherName));
    if (!DelegateProperty)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher property not found: %s. Compile or recreate the dispatcher before adding a bind node."), *DispatcherName));
    }
    if (!DelegateProperty->HasAllPropertyFlags(CPF_BlueprintAssignable))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher is not BlueprintAssignable: %s"), *DispatcherName));
    }
    if (!DelegateProperty->SignatureFunction)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Event dispatcher signature is not available: %s"), *DispatcherName));
    }

    UK2Node_AddDelegate* BindNode = NewObject<UK2Node_AddDelegate>(TargetGraph);
    if (!BindNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create Event Dispatcher bind node"));
    }

    BindNode->SetFromProperty(DelegateProperty, IsSelfContextForDelegateProperty(Blueprint, DelegateProperty), DelegateProperty->GetOwnerClass());
    if (!BindNode->IsCompatibleWithGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Event Dispatcher bind nodes are only supported in event or function graphs"));
    }

    BindNode->NodePosX = NodePosition.X;
    BindNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(BindNode, true);
    BindNode->CreateNewGuid();
    BindNode->PostPlacedNewNode();
    BindNode->AllocateDefaultPins();
    BindNode->ReconstructNode();

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(BindNode, true);
    ResultObj->SetStringField(TEXT("dispatcher_name"), DispatcherName);
    ResultObj->SetStringField(TEXT("signature_function"), DelegateProperty->SignatureFunction->GetPathName());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEventDispatcherUnbindNode(const TSharedPtr<FJsonObject>& Params)
{
    FEventDispatcherNodeRequest Request;
    FString Error;
    if (!ResolveEventDispatcherNodeRequest(Params, TEXT("unbind"), Request, Error))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(Error);
    }

    return CreateEventDispatcherLifecycleNode<UK2Node_RemoveDelegate>(
        Request,
        TEXT("unbind"),
        false,
        true,
        false);
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEventDispatcherClearNode(const TSharedPtr<FJsonObject>& Params)
{
    FEventDispatcherNodeRequest Request;
    FString Error;
    if (!ResolveEventDispatcherNodeRequest(Params, TEXT("clear"), Request, Error))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(Error);
    }

    return CreateEventDispatcherLifecycleNode<UK2Node_ClearDelegate>(
        Request,
        TEXT("clear"),
        false,
        true,
        false);
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEventDispatcherAssignNode(const TSharedPtr<FJsonObject>& Params)
{
    FEventDispatcherNodeRequest Request;
    FString Error;
    if (!ResolveEventDispatcherNodeRequest(Params, TEXT("assign"), Request, Error))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(Error);
    }

    return CreateEventDispatcherLifecycleNode<UK2Node_AssignDelegate>(
        Request,
        TEXT("assign"),
        true,
        false,
        true);
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintFunctionParameter(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString ParameterName;
    if (!Params->TryGetStringField(TEXT("parameter_name"), ParameterName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'parameter_name' parameter"));
    }

    FString ParameterType;
    if (!Params->TryGetStringField(TEXT("parameter_type"), ParameterType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'parameter_type' parameter"));
    }

    FString Direction;
    Params->TryGetStringField(TEXT("direction"), Direction);
    const bool bIsOutputParameter = Direction.Equals(TEXT("output"), ESearchCase::IgnoreCase) || Direction.Equals(TEXT("return"), ESearchCase::IgnoreCase);
    if (!bIsOutputParameter && !Direction.IsEmpty() && !Direction.Equals(TEXT("input"), ESearchCase::IgnoreCase))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'direction' must be 'input' or 'output'"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (GetBlueprintGraphType(Blueprint, TargetGraph) != TEXT("function"))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Function parameters are only supported in function graphs"));
    }

    FEdGraphPinType PinType;
    FString TypeError;
    if (!BuildPinTypeFromDescriptor(ParameterType, Params, TEXT("type_object"), PinType, TypeError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TypeError);
    }

    const TSharedPtr<FJsonValue> DefaultJsonValue = Params->TryGetField(TEXT("default_value"));
    FString DefaultValue;
    if (DefaultJsonValue.IsValid())
    {
        FString DefaultError;
        if (!GetPinDefaultStringForTypeChecked(DefaultJsonValue, PinType, DefaultValue, DefaultError))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for function parameter '%s': %s"), *ParameterName, *DefaultError));
        }
    }

    UK2Node_FunctionEntry* EntryNode = Cast<UK2Node_FunctionEntry>(FBlueprintEditorUtils::GetEntryNode(TargetGraph));
    if (!EntryNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Function entry node not found"));
    }

    UK2Node_EditablePinBase* EditableNode = EntryNode;
    EEdGraphPinDirection PinDirection = EGPD_Output;
    if (bIsOutputParameter)
    {
        UK2Node_FunctionResult* ReturnNode = FBlueprintEditorUtils::FindOrCreateFunctionResultNode(EntryNode);
        if (!ReturnNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create function return node"));
        }
        EditableNode = ReturnNode;
        PinDirection = EGPD_Input;
    }

    if (FUnrealMCPCommonUtils::FindPin(EditableNode, ParameterName, PinDirection))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Function parameter already exists: %s"), *ParameterName));
    }

    FText PinError;
    if (!EditableNode->CanCreateUserDefinedPin(PinType, PinDirection, PinError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(PinError.ToString());
    }

    UEdGraphPin* NewPin = EditableNode->CreateUserDefinedPin(FName(*ParameterName), PinType, PinDirection, false);
    if (!NewPin)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to add function parameter: %s"), *ParameterName));
    }

    if (DefaultJsonValue.IsValid())
    {
        TSharedPtr<FUserPinInfo> PinInfo = FindUserDefinedPinInfo(EditableNode, FName(*ParameterName), PinDirection);
        if (!PinInfo.IsValid() || !EditableNode->ModifyUserDefinedPinDefaultValue(PinInfo, DefaultValue))
        {
            EditableNode->RemoveUserDefinedPinByName(FName(*ParameterName));
            EditableNode->ReconstructNode();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to set default value for function parameter: %s"), *ParameterName));
        }
    }

    EditableNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(EditableNode, true);
    ResultObj->SetStringField(TEXT("parameter_name"), ParameterName);
    ResultObj->SetStringField(TEXT("direction"), bIsOutputParameter ? TEXT("output") : TEXT("input"));
    ResultObj->SetStringField(TEXT("default_value"), DefaultValue);
    ResultObj->SetObjectField(TEXT("pin_type"), PinTypeToJson(PinType));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintLocalVariable(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString VariableName;
    if (!Params->TryGetStringField(TEXT("variable_name"), VariableName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_name' parameter"));
    }

    FString VariableType;
    if (!Params->TryGetStringField(TEXT("variable_type"), VariableType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_type' parameter"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (GetBlueprintGraphType(Blueprint, TargetGraph) != TEXT("function"))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Local variables are only supported in function graphs"));
    }
    if (!FBlueprintEditorUtils::DoesSupportLocalVariables(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Target graph does not support local variables"));
    }

    FEdGraphPinType PinType;
    FString TypeError;
    if (!BuildPinTypeFromDescriptor(VariableType, Params, TEXT("type_object"), PinType, TypeError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TypeError);
    }

    if (FBlueprintEditorUtils::FindLocalVariable(Blueprint, TargetGraph, FName(*VariableName)))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Local variable already exists: %s"), *VariableName));
    }

    FString DefaultValue;
    if (const TSharedPtr<FJsonValue> DefaultJsonValue = Params->TryGetField(TEXT("default_value")))
    {
        FString DefaultError;
        if (!GetPinDefaultStringForTypeChecked(DefaultJsonValue, PinType, DefaultValue, DefaultError))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for local variable '%s': %s"), *VariableName, *DefaultError));
        }
    }

    if (!FBlueprintEditorUtils::AddLocalVariable(Blueprint, TargetGraph, FName(*VariableName), PinType, DefaultValue))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Failed to add local variable: %s"), *VariableName));
    }

    if (FBPVariableDescription* LocalVariable = FBlueprintEditorUtils::FindLocalVariable(Blueprint, TargetGraph, FName(*VariableName)))
    {
        if (Params->HasField(TEXT("category")))
        {
            LocalVariable->Category = FText::FromString(GetStringParam(Params, TEXT("category")));
        }
        if (Params->HasField(TEXT("tooltip")))
        {
            LocalVariable->SetMetaData(TEXT("Tooltip"), GetStringParam(Params, TEXT("tooltip")));
        }
    }

    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("variable_name"), VariableName);
    ResultObj->SetStringField(TEXT("variable_type"), VariableType);
    ResultObj->SetStringField(TEXT("default_value"), DefaultValue);
    ResultObj->SetObjectField(TEXT("pin_type"), PinTypeToJson(PinType));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintBranchNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_IfThenElse* BranchNode = AddK2NodeToGraph<UK2Node_IfThenElse>(TargetGraph, NodePosition);
    if (!BranchNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create branch node"));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(BranchNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintSequenceNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    int32 OutputCount = 2;
    if (Params->HasField(TEXT("output_count")))
    {
        OutputCount = FMath::Max(2, FMath::RoundToInt(Params->GetNumberField(TEXT("output_count"))));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_ExecutionSequence* SequenceNode = AddK2NodeToGraph<UK2Node_ExecutionSequence>(TargetGraph, NodePosition);
    if (!SequenceNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create sequence node"));
    }

    int32 CurrentExecOutputs = 0;
    for (UEdGraphPin* Pin : SequenceNode->Pins)
    {
        if (Pin && Pin->Direction == EGPD_Output && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Exec)
        {
            ++CurrentExecOutputs;
        }
    }

    while (CurrentExecOutputs < OutputCount)
    {
        SequenceNode->AddInputPin();
        ++CurrentExecOutputs;
    }

    SequenceNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(SequenceNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintReturnNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FVector2D NodePosition(320.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (GetBlueprintGraphType(Blueprint, TargetGraph) != TEXT("function"))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Return nodes are only supported in function graphs"));
    }

    UK2Node_EditablePinBase* EntryNode = FBlueprintEditorUtils::GetEntryNode(TargetGraph);
    if (!EntryNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Function entry node not found"));
    }

    UK2Node_FunctionResult* ReturnNode = FBlueprintEditorUtils::FindOrCreateFunctionResultNode(EntryNode);
    if (!ReturnNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create function return node"));
    }

    ReturnNode->NodePosX = NodePosition.X;
    ReturnNode->NodePosY = NodePosition.Y;
    ReturnNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(ReturnNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintDynamicCastNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString TargetClassName;
    if (!Params->TryGetStringField(TEXT("target_class"), TargetClassName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'target_class' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UClass* TargetClass = LoadClassForPin(TargetClassName);
    if (!TargetClass || !TargetClass->IsChildOf(UObject::StaticClass()))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Target class not found or not a UObject class: %s"), *TargetClassName));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_DynamicCast* CastNode = NewObject<UK2Node_DynamicCast>(TargetGraph);
    if (!CastNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create dynamic cast node"));
    }

    CastNode->TargetType = TargetClass;
    CastNode->NodePosX = NodePosition.X;
    CastNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(CastNode, true);
    CastNode->CreateNewGuid();
    CastNode->PostPlacedNewNode();
    CastNode->AllocateDefaultPins();
    if (Params->HasField(TEXT("pure")))
    {
        CastNode->SetPurity(Params->GetBoolField(TEXT("pure")));
    }
    CastNode->ReconstructNode();

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(CastNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintLoopNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    const FString LoopType = GetStringParam(Params, TEXT("loop_type"), TEXT("for_loop"));
    FString LoopTypeError;
    const FName MacroName = ResolveLoopMacroName(LoopType, LoopTypeError);
    if (MacroName.IsNone())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(LoopTypeError);
    }

    FString MacroError;
    UEdGraph* MacroGraph = ResolveStandardMacroGraph(MacroName.ToString(), MacroError);
    if (!MacroGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MacroError);
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    UK2Node_MacroInstance* LoopNode = NewObject<UK2Node_MacroInstance>(TargetGraph);
    if (!LoopNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create loop macro node"));
    }

    LoopNode->SetMacroGraph(MacroGraph);
    LoopNode->NodePosX = NodePosition.X;
    LoopNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(LoopNode, true);
    LoopNode->CreateNewGuid();
    LoopNode->PostPlacedNewNode();
    LoopNode->AllocateDefaultPins();

    TSharedPtr<FJsonObject> AppliedDefaults = MakeShared<FJsonObject>();
    FString DefaultError;
    if (!ApplyOptionalIntegerPinDefault(Params, TEXT("first_index"), LoopNode, TEXT("FirstIndex"), K2Schema, AppliedDefaults, DefaultError) ||
        !ApplyOptionalIntegerPinDefault(Params, TEXT("last_index"), LoopNode, TEXT("LastIndex"), K2Schema, AppliedDefaults, DefaultError))
    {
        LoopNode->DestroyNode();
        return FUnrealMCPCommonUtils::CreateErrorResponse(DefaultError);
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(LoopNode, true);
    ResultObj->SetStringField(TEXT("loop_type"), TEXT("for_loop"));
    ResultObj->SetStringField(TEXT("macro_name"), MacroName.ToString());
    ResultObj->SetStringField(TEXT("macro_graph"), MacroGraph->GetPathName());
    ResultObj->SetObjectField(TEXT("pin_defaults_applied"), AppliedDefaults);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintArrayFunctionNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString Operation;
    if (!Params->TryGetStringField(TEXT("operation"), Operation))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'operation' parameter"));
    }

    FString ElementTypeName;
    if (!Params->TryGetStringField(TEXT("element_type"), ElementTypeName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'element_type' parameter"));
    }

    FString OperationError;
    const FName FunctionName = ResolveArrayOperationFunctionName(Operation, OperationError);
    if (FunctionName.IsNone())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(OperationError);
    }

    FEdGraphPinType ElementPinType;
    FString TypeError;
    if (!BuildPinTypeFromDescriptor(ElementTypeName, Params, TEXT("type_object"), ElementPinType, TypeError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TypeError);
    }
    ElementPinType.ContainerType = EPinContainerType::None;
    ElementPinType.bIsReference = false;

    UFunction* ArrayFunction = UKismetArrayLibrary::StaticClass()->FindFunctionByName(FunctionName);
    if (!ArrayFunction)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Array function not found: %s"), *FunctionName.ToString()));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    UK2Node_CallArrayFunction* ArrayNode = NewObject<UK2Node_CallArrayFunction>(TargetGraph);
    if (!ArrayNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create array function node"));
    }

    ArrayNode->SetFromFunction(ArrayFunction);
    ArrayNode->NodePosX = NodePosition.X;
    ArrayNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(ArrayNode, true);
    ArrayNode->CreateNewGuid();
    ArrayNode->PostPlacedNewNode();
    ArrayNode->AllocateDefaultPins();

    FString ArrayTypeError;
    if (!ApplyPinTypeToArrayFunctionNode(ArrayNode, ElementPinType, ArrayTypeError))
    {
        ArrayNode->DestroyNode();
        return FUnrealMCPCommonUtils::CreateErrorResponse(ArrayTypeError);
    }

    TSharedPtr<FJsonObject> AppliedDefaults = MakeShared<FJsonObject>();
    const TSharedPtr<FJsonObject>* ParamDefaultsObj = nullptr;
    bool bHasParamDefaults = Params->TryGetObjectField(TEXT("param_defaults"), ParamDefaultsObj);
    if (!bHasParamDefaults)
    {
        bHasParamDefaults = Params->TryGetObjectField(TEXT("params"), ParamDefaultsObj);
    }

    if (bHasParamDefaults && ParamDefaultsObj && ParamDefaultsObj->IsValid())
    {
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Param : (*ParamDefaultsObj)->Values)
        {
            if (Param.Key.Equals(TEXT("TargetArray"), ESearchCase::IgnoreCase))
            {
                ArrayNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("TargetArray must be connected from an array pin; defaults are not supported"));
            }

            UEdGraphPin* ParamPin = FUnrealMCPCommonUtils::FindPin(ArrayNode, Param.Key, EGPD_Input);
            if (!ParamPin)
            {
                ArrayNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Array function parameter pin not found: %s"), *Param.Key));
            }

            FString AppliedValue;
            FString DefaultError;
            if (!ApplyPinDefaultValueChecked(ParamPin, Param.Value, K2Schema, AppliedValue, DefaultError))
            {
                ArrayNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for array function parameter '%s': %s"), *Param.Key, *DefaultError));
            }

            ArrayNode->PinDefaultValueChanged(ParamPin);
            AppliedDefaults->SetStringField(Param.Key, AppliedValue);
        }
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(ArrayNode, true);
    ResultObj->SetStringField(TEXT("operation"), NormalizeTypeName(Operation));
    ResultObj->SetStringField(TEXT("function_name"), ArrayFunction->GetName());
    ResultObj->SetStringField(TEXT("function_class"), UKismetArrayLibrary::StaticClass()->GetPathName());
    ResultObj->SetObjectField(TEXT("element_pin_type"), PinTypeToJson(ElementPinType));
    ResultObj->SetObjectField(TEXT("param_defaults_applied"), AppliedDefaults);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintMakeArrayNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString ElementTypeName;
    if (!Params->TryGetStringField(TEXT("element_type"), ElementTypeName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'element_type' parameter"));
    }

    FEdGraphPinType ElementPinType;
    FString TypeError;
    if (!BuildPinTypeFromDescriptor(ElementTypeName, Params, TEXT("type_object"), ElementPinType, TypeError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TypeError);
    }
    if (ElementPinType.IsArray() || GetBoolParam(Params, TEXT("is_array"), false))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Nested array literals are not supported"));
    }
    ElementPinType.ContainerType = EPinContainerType::None;
    ElementPinType.PinValueType = FEdGraphTerminalType();
    ElementPinType.bIsReference = false;

    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    bool bHasValues = false;
    int32 InputCount = 0;
    FString InputError;
    if (!ResolveMakeArrayInputs(Params, Values, bHasValues, InputCount, InputError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(InputError);
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    UK2Node_MakeArray* MakeArrayNode = NewObject<UK2Node_MakeArray>(TargetGraph);
    if (!MakeArrayNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create make array node"));
    }

    MakeArrayNode->NumInputs = InputCount;
    MakeArrayNode->NodePosX = NodePosition.X;
    MakeArrayNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(MakeArrayNode, true);
    MakeArrayNode->CreateNewGuid();
    MakeArrayNode->PostPlacedNewNode();
    MakeArrayNode->AllocateDefaultPins();

    FString ArrayTypeError;
    if (!ApplyPinTypeToMakeArrayNode(MakeArrayNode, ElementPinType, ArrayTypeError))
    {
        MakeArrayNode->DestroyNode();
        return FUnrealMCPCommonUtils::CreateErrorResponse(ArrayTypeError);
    }

    TSharedPtr<FJsonObject> AppliedDefaults = MakeShared<FJsonObject>();
    if (bHasValues && Values)
    {
        for (int32 Index = 0; Index < Values->Num(); ++Index)
        {
            const FString PinName = FString::Printf(TEXT("[%d]"), Index);
            UEdGraphPin* InputPin = FUnrealMCPCommonUtils::FindPin(MakeArrayNode, PinName, EGPD_Input);
            if (!InputPin)
            {
                MakeArrayNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Make array input pin not found: %s"), *PinName));
            }

            FString AppliedValue;
            FString DefaultError;
            if (!ApplyPinDefaultValueChecked(InputPin, (*Values)[Index], K2Schema, AppliedValue, DefaultError))
            {
                MakeArrayNode->DestroyNode();
                return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for make array pin '%s': %s"), *PinName, *DefaultError));
            }

            MakeArrayNode->PinDefaultValueChanged(InputPin);
            AppliedDefaults->SetStringField(PinName, AppliedValue);
        }
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(MakeArrayNode, true);
    ResultObj->SetObjectField(TEXT("element_pin_type"), PinTypeToJson(ElementPinType));
    ResultObj->SetNumberField(TEXT("input_count"), InputCount);
    ResultObj->SetObjectField(TEXT("values_applied"), AppliedDefaults);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintInputActionNode(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString ActionName;
    if (!Params->TryGetStringField(TEXT("action_name"), ActionName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'action_name' parameter"));
    }

    // Get position parameters (optional)
    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // Create the input action node
    UK2Node_InputAction* InputActionNode = FUnrealMCPCommonUtils::CreateInputActionNode(TargetGraph, ActionName, NodePosition);
    if (!InputActionNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create input action node"));
    }

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("node_id"), InputActionNode->NodeGuid.ToString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintSelfReference(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    // Get position parameters (optional)
    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // Create the self node
    UK2Node_Self* SelfNode = FUnrealMCPCommonUtils::CreateSelfReferenceNode(TargetGraph, NodePosition);
    if (!SelfNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create self node"));
    }

    // Mark the blueprint as modified
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("node_id"), SelfNode->NodeGuid.ToString());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleResolveBlueprint(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> CandidateArray;

    const TArray<FString> CandidatePaths = FUnrealMCPCommonUtils::FindBlueprintAssetPaths(BlueprintName);
    for (const FString& CandidatePath : CandidatePaths)
    {
        CandidateArray.Add(MakeShared<FJsonValueString>(CandidatePath));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    ResultObj->SetBoolField(TEXT("resolved"), Blueprint != nullptr);
    if (Blueprint)
    {
        ResultObj->SetStringField(TEXT("asset_path"), Blueprint->GetPathName());
        ResultObj->SetStringField(TEXT("name"), Blueprint->GetName());
    }
    ResultObj->SetArrayField(TEXT("candidates"), CandidateArray);

    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleListBlueprintGraphs(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString GraphType;
    Params->TryGetStringField(TEXT("graph_type"), GraphType);
    const FString NormalizedType = NormalizeGraphType(GraphType);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    TArray<UEdGraph*> Graphs;
    Blueprint->GetAllGraphs(Graphs);

    TArray<TSharedPtr<FJsonValue>> GraphArray;
    for (UEdGraph* Graph : Graphs)
    {
        if (!Graph)
        {
            continue;
        }

        const FString CurrentType = GetBlueprintGraphType(Blueprint, Graph);
        if (!NormalizedType.IsEmpty() && NormalizedType != TEXT("any") && CurrentType != NormalizedType)
        {
            continue;
        }

        GraphArray.Add(MakeShared<FJsonValueObject>(GraphToJson(Blueprint, Graph)));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("blueprint"), Blueprint->GetPathName());
    ResultObj->SetArrayField(TEXT("graphs"), GraphArray);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleResolveBlueprintGraph(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    bool bCreateIfMissing = false;
    if (Params->HasField(TEXT("create_if_missing")))
    {
        bCreateIfMissing = Params->GetBoolField(TEXT("create_if_missing"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    bool bCreated = false;
    FString GraphError;
    UEdGraph* Graph = ResolveBlueprintGraph(Blueprint, Params, bCreateIfMissing, bCreated, GraphError);
    if (!Graph)
    {
        TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
        ResultObj->SetStringField(TEXT("blueprint"), Blueprint->GetPathName());
        ResultObj->SetBoolField(TEXT("resolved"), false);
        ResultObj->SetBoolField(TEXT("created"), false);
        ResultObj->SetStringField(TEXT("error"), GraphError);
        return ResultObj;
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("blueprint"), Blueprint->GetPathName());
    ResultObj->SetBoolField(TEXT("resolved"), true);
    ResultObj->SetBoolField(TEXT("created"), bCreated);
    AddGraphField(ResultObj, Blueprint, Graph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleListBlueprintNodes(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString NodeType;
    Params->TryGetStringField(TEXT("node_type"), NodeType);

    FString TitleContains;
    Params->TryGetStringField(TEXT("title_contains"), TitleContains);

    bool bIncludePins = true;
    if (Params->HasField(TEXT("include_pins")))
    {
        bIncludePins = Params->GetBoolField(TEXT("include_pins"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    TArray<TSharedPtr<FJsonValue>> Nodes;
    for (UEdGraphNode* Node : TargetGraph->Nodes)
    {
        if (MatchesNodeFilter(Node, NodeType, TitleContains))
        {
            Nodes.Add(MakeShared<FJsonValueObject>(NodeToJson(Node, bIncludePins)));
        }
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("blueprint"), Blueprint->GetPathName());
    ResultObj->SetStringField(TEXT("graph_name"), TargetGraph->GetName());
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    ResultObj->SetArrayField(TEXT("nodes"), Nodes);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleInspectAnimGraphNodeSettings(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString NodeId;
    Params->TryGetStringField(TEXT("node_id"), NodeId);

    FString NodeType;
    Params->TryGetStringField(TEXT("node_type"), NodeType);

    FString TitleContains;
    Params->TryGetStringField(TEXT("title_contains"), TitleContains);

    bool bIncludePins = true;
    if (Params->HasField(TEXT("include_pins")))
    {
        bIncludePins = Params->GetBoolField(TEXT("include_pins"));
    }

    int32 MaxDepth = 4;
    if (Params->HasField(TEXT("max_depth")))
    {
        MaxDepth = FMath::Clamp(static_cast<int32>(Params->GetIntegerField(TEXT("max_depth"))), 1, 8);
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    TArray<TSharedPtr<FJsonValue>> Nodes;
    for (UEdGraphNode* Node : TargetGraph->Nodes)
    {
        if (!Node)
        {
            continue;
        }
        if (!NodeId.IsEmpty() && Node->NodeGuid.ToString() != NodeId)
        {
            continue;
        }
        if (!MatchesNodeFilter(Node, NodeType, TitleContains))
        {
            continue;
        }

        TSharedPtr<FJsonObject> NodeObject = NodeToJson(Node, bIncludePins);
        if (UAnimGraphNode_Base* AnimGraphNode = Cast<UAnimGraphNode_Base>(Node))
        {
            NodeObject->SetObjectField(TEXT("settings"), AnimGraphNodeSettingsToJson(AnimGraphNode, MaxDepth));
        }
        else
        {
            TSharedPtr<FJsonObject> SettingsObject = MakeShared<FJsonObject>();
            SettingsObject->SetBoolField(TEXT("has_anim_node_struct"), false);
            NodeObject->SetObjectField(TEXT("settings"), SettingsObject);
        }
        Nodes.Add(MakeShared<FJsonValueObject>(NodeObject));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("blueprint"), Blueprint->GetPathName());
    ResultObj->SetStringField(TEXT("graph_name"), TargetGraph->GetName());
    ResultObj->SetNumberField(TEXT("max_depth"), MaxDepth);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    ResultObj->SetArrayField(TEXT("nodes"), Nodes);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleInspectAnimStateMachineTransitions(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    const FString StateMachineFilter = GetStringParam(Params, TEXT("state_machine_name"));
    const bool bIncludePins = GetBoolParam(Params, TEXT("include_pins"), true);
    const bool bIncludeRuleGraphNodes = GetBoolParam(Params, TEXT("include_rule_graph_nodes"), true);
    const bool bIncludeStateNodes = GetBoolParam(Params, TEXT("include_state_nodes"), true);
    const int32 MaxRuleGraphNodes = FMath::Clamp(
        Params->HasField(TEXT("max_rule_graph_nodes")) ? Params->GetIntegerField(TEXT("max_rule_graph_nodes")) : 256,
        -1,
        2048);

    TArray<UAnimGraphNode_StateMachineBase*> StateMachineNodes;
    FBlueprintEditorUtils::GetAllNodesOfClass<UAnimGraphNode_StateMachineBase>(Blueprint, StateMachineNodes);

    TArray<TSharedPtr<FJsonValue>> StateMachineValues;
    int32 TotalTransitionCount = 0;
    for (UAnimGraphNode_StateMachineBase* StateMachineNode : StateMachineNodes)
    {
        if (!StateMachineNode)
        {
            continue;
        }

        const FString StateMachineName = StateMachineNode->GetStateMachineName();
        const FString StateMachineTitle = StateMachineNode->GetNodeTitle(ENodeTitleType::FullTitle).ToString();
        if (!StateMachineFilter.IsEmpty() &&
            !StateMachineName.Contains(StateMachineFilter, ESearchCase::IgnoreCase) &&
            !StateMachineTitle.Contains(StateMachineFilter, ESearchCase::IgnoreCase))
        {
            continue;
        }

        UAnimationStateMachineGraph* StateMachineGraph = StateMachineNode->EditorStateMachineGraph;
        TSharedPtr<FJsonObject> StateMachineObject = MakeShared<FJsonObject>();
        StateMachineObject->SetStringField(TEXT("state_machine_name"), StateMachineName);
        StateMachineObject->SetObjectField(TEXT("state_machine_node"), NodeToJson(StateMachineNode, bIncludePins));
        StateMachineObject->SetObjectField(TEXT("state_machine_graph"), GraphToJson(Blueprint, StateMachineGraph));

        TArray<TSharedPtr<FJsonValue>> StateValues;
        TArray<TSharedPtr<FJsonValue>> TransitionValues;
        if (StateMachineGraph)
        {
            for (UEdGraphNode* GraphNode : StateMachineGraph->Nodes)
            {
                if (!GraphNode)
                {
                    continue;
                }

                if (UAnimStateTransitionNode* TransitionNode = Cast<UAnimStateTransitionNode>(GraphNode))
                {
                    UAnimStateNodeBase* PreviousState = TransitionNode->GetPreviousState();
                    UAnimStateNodeBase* NextState = TransitionNode->GetNextState();

                    TSharedPtr<FJsonObject> TransitionObject = MakeShared<FJsonObject>();
                    TransitionObject->SetStringField(TEXT("transition_id"), TransitionNode->NodeGuid.ToString());
                    TransitionObject->SetStringField(TEXT("transition_title"), TransitionNode->GetNodeTitle(ENodeTitleType::FullTitle).ToString());
                    TransitionObject->SetObjectField(TEXT("transition_node"), NodeToJson(TransitionNode, bIncludePins));
                    TransitionObject->SetObjectField(TEXT("source_state"), AnimStateNodeToJson(Blueprint, PreviousState, false));
                    TransitionObject->SetObjectField(TEXT("target_state"), AnimStateNodeToJson(Blueprint, NextState, false));
                    TransitionObject->SetObjectField(TEXT("settings"), AnimStateTransitionSettingsToJson(TransitionNode));

                    if (UEdGraph* BoundGraph = TransitionNode->GetBoundGraph())
                    {
                        TransitionObject->SetObjectField(
                            TEXT("rule_graph"),
                            bIncludeRuleGraphNodes
                                ? TransitionGraphNodesToJson(Blueprint, BoundGraph, bIncludePins, MaxRuleGraphNodes)
                                : GraphToJson(Blueprint, BoundGraph));
                    }

                    if (UEdGraph* CustomTransitionGraph = TransitionNode->GetCustomTransitionGraph())
                    {
                        TransitionObject->SetObjectField(TEXT("custom_transition_graph"), GraphToJson(Blueprint, CustomTransitionGraph));
                    }

                    TransitionValues.Add(MakeShared<FJsonValueObject>(TransitionObject));
                    ++TotalTransitionCount;
                }
                else if (bIncludeStateNodes)
                {
                    if (UAnimStateNodeBase* StateNode = Cast<UAnimStateNodeBase>(GraphNode))
                    {
                        StateValues.Add(MakeShared<FJsonValueObject>(AnimStateNodeToJson(Blueprint, StateNode, false)));
                    }
                }
            }
        }

        StateMachineObject->SetArrayField(TEXT("states"), StateValues);
        StateMachineObject->SetArrayField(TEXT("transitions"), TransitionValues);
        StateMachineObject->SetNumberField(TEXT("state_count"), StateValues.Num());
        StateMachineObject->SetNumberField(TEXT("transition_count"), TransitionValues.Num());
        StateMachineValues.Add(MakeShared<FJsonValueObject>(StateMachineObject));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), true);
    ResultObj->SetStringField(TEXT("blueprint_name"), BlueprintName);
    ResultObj->SetStringField(TEXT("blueprint_path"), Blueprint->GetPathName());
    ResultObj->SetStringField(TEXT("state_machine_filter"), StateMachineFilter);
    ResultObj->SetNumberField(TEXT("state_machine_count"), StateMachineValues.Num());
    ResultObj->SetNumberField(TEXT("transition_count"), TotalTransitionCount);
    ResultObj->SetBoolField(TEXT("read_only"), true);
    ResultObj->SetArrayField(TEXT("state_machines"), StateMachineValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleControlRigDirectGateProbe(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    const FString ShouldTracePropertyName = GetStringParam(Params, TEXT("should_trace_property"), TEXT("ShouldDoIKTrace"));
    const FString InteractionLocationPropertyName = GetStringParam(Params, TEXT("interaction_location_property"), TEXT("InteractionWorldLocation"));
    const TArray<FControlRigDirectProbeCase> ProbeCases = ParseControlRigProbeCases(Params, ShouldTracePropertyName, InteractionLocationPropertyName);

    const TArray<FString> DefaultSampleElements = {
        TEXT("pelvis"),
        TEXT("thigh_l"),
        TEXT("calf_l"),
        TEXT("foot_l"),
        TEXT("thigh_r"),
        TEXT("calf_r"),
        TEXT("foot_r"),
        TEXT("IK_foot_L"),
        TEXT("IK_foot_R"),
        TEXT("head_ctrl")
    };
    const TArray<FString> SampleElements = GetStringArrayParam(Params, TEXT("sample_elements"), DefaultSampleElements);

    const TArray<FString> DefaultExecuteEvents = {
        TEXT("Construction"),
        TEXT("Forwards Solve"),
        TEXT("Post Forwards Solve")
    };
    const TArray<FString> ExecuteEvents = GetStringArrayParam(Params, TEXT("execute_events"), DefaultExecuteEvents);

    TArray<TSharedPtr<FJsonValue>> CaseValues;
    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;
    TMap<FString, FTransform> BaselineTransforms;
    bool bHasBaseline = false;
    FString BaselineCaseName;
    FString ResolvedAssetPath;
    FString ResolvedClassPath;

    for (const FControlRigDirectProbeCase& ProbeCase : ProbeCases)
    {
        FString CaseAssetPath;
        FString CaseClassPath;
        FString CreateError;
        UControlRig* ControlRig = CreateTransientControlRigFromParams(Params, CaseAssetPath, CaseClassPath, CreateError);
        if (!ControlRig)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(CreateError);
        }

        if (ResolvedAssetPath.IsEmpty())
        {
            ResolvedAssetPath = CaseAssetPath;
        }
        if (ResolvedClassPath.IsEmpty())
        {
            ResolvedClassPath = CaseClassPath;
        }

        TSharedPtr<FJsonObject> CaseObject = MakeShared<FJsonObject>();
        CaseObject->SetStringField(TEXT("name"), ProbeCase.Name);
        CaseObject->SetStringField(TEXT("control_rig_class"), CaseClassPath);

        TArray<TSharedPtr<FJsonValue>> CaseErrorValues;
        TArray<TSharedPtr<FJsonValue>> CaseWarningValues;
        auto AddCaseError = [&CaseErrorValues, &ErrorValues, &ProbeCase](const FString& ErrorText)
        {
            CaseErrorValues.Add(MakeShared<FJsonValueString>(ErrorText));
            ErrorValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%s: %s"), *ProbeCase.Name, *ErrorText)));
        };
        auto AddCaseWarning = [&CaseWarningValues, &WarningValues, &ProbeCase](const FString& WarningText)
        {
            CaseWarningValues.Add(MakeShared<FJsonValueString>(WarningText));
            WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%s: %s"), *ProbeCase.Name, *WarningText)));
        };

        ControlRig->Initialize(true);
        URigHierarchy* Hierarchy = ControlRig->GetHierarchy();
        if (!Hierarchy)
        {
            AddCaseError(TEXT("ControlRig hierarchy is null after Initialize"));
            CaseObject->SetArrayField(TEXT("errors"), CaseErrorValues);
            CaseObject->SetArrayField(TEXT("warnings"), CaseWarningValues);
            CaseValues.Add(MakeShared<FJsonValueObject>(CaseObject));
            continue;
        }

        TSharedPtr<FJsonObject> PropertyInputsObject = MakeShared<FJsonObject>();
        TSharedPtr<FJsonObject> PropertyEchoObject = MakeShared<FJsonObject>();
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : ProbeCase.PropertyValues)
        {
            PropertyInputsObject->SetField(Pair.Key, Pair.Value);
            FString PropertyError;
            if (!SetUObjectPropertyFromJson(ControlRig, Pair.Key, Pair.Value, PropertyError))
            {
                AddCaseError(PropertyError);
                continue;
            }
            PropertyEchoObject->SetField(Pair.Key, GetUObjectPropertyJson(ControlRig, Pair.Key));
        }

        TSharedPtr<FJsonObject> CurveInputsObject = MakeShared<FJsonObject>();
        TSharedPtr<FJsonObject> CurveEchoAfterSetObject = MakeShared<FJsonObject>();
        for (const TPair<FName, double>& Pair : ProbeCase.CurveValues)
        {
            CurveInputsObject->SetNumberField(Pair.Key.ToString(), Pair.Value);
            const FRigElementKey CurveKey(Pair.Key, ERigElementType::Curve);
            if (!Hierarchy->Contains(CurveKey))
            {
                AddCaseError(FString::Printf(TEXT("Curve '%s' not found in ControlRig hierarchy"), *Pair.Key.ToString()));
                continue;
            }

            Hierarchy->SetCurveValue(CurveKey, static_cast<float>(Pair.Value), false);
            CurveEchoAfterSetObject->SetNumberField(Pair.Key.ToString(), Hierarchy->GetCurveValue(CurveKey));
        }

        TArray<TSharedPtr<FJsonValue>> ExecuteResultValues;
        for (const FString& EventName : ExecuteEvents)
        {
            TSharedPtr<FJsonObject> ExecuteObject = MakeShared<FJsonObject>();
            ExecuteObject->SetStringField(TEXT("event"), EventName);
            const bool bExecuted = ControlRig->Execute(FName(*EventName));
            ExecuteObject->SetBoolField(TEXT("success"), bExecuted);
            ExecuteResultValues.Add(MakeShared<FJsonValueObject>(ExecuteObject));
            if (!bExecuted)
            {
                const FString WarningText = FString::Printf(TEXT("ControlRig Execute returned false for event '%s'"), *EventName);
                ExecuteObject->SetStringField(TEXT("warning"), WarningText);
                AddCaseWarning(WarningText);
            }
        }

        TSharedPtr<FJsonObject> CurveEchoAfterExecuteObject = MakeShared<FJsonObject>();
        for (const TPair<FName, double>& Pair : ProbeCase.CurveValues)
        {
            const FRigElementKey CurveKey(Pair.Key, ERigElementType::Curve);
            if (Hierarchy->Contains(CurveKey))
            {
                CurveEchoAfterExecuteObject->SetNumberField(Pair.Key.ToString(), Hierarchy->GetCurveValue(CurveKey));
            }
        }

        TSharedPtr<FJsonObject> TransformObject = MakeShared<FJsonObject>();
        TMap<FString, FTransform> CaseTransforms;
        for (const FString& ElementSpec : SampleElements)
        {
            FRigElementKey ElementKey;
            TSharedPtr<FJsonObject> SampleObject = MakeShared<FJsonObject>();
            SampleObject->SetStringField(TEXT("requested"), ElementSpec);

            if (!ResolveRigElementKey(Hierarchy, ElementSpec, ElementKey))
            {
                SampleObject->SetBoolField(TEXT("valid"), false);
                SampleObject->SetStringField(TEXT("error"), FString::Printf(TEXT("Rig element not found: %s"), *ElementSpec));
                TransformObject->SetObjectField(ElementSpec, SampleObject);
                continue;
            }

            SampleObject->SetBoolField(TEXT("valid"), true);
            SampleObject->SetStringField(TEXT("name"), ElementKey.Name.ToString());
            SampleObject->SetStringField(TEXT("type"), RigElementTypeToString(ElementKey.Type));

            if (ElementKey.Type == ERigElementType::Curve)
            {
                SampleObject->SetNumberField(TEXT("curve_value"), Hierarchy->GetCurveValue(ElementKey));
                SampleObject->SetStringField(TEXT("note"), TEXT("Curve elements do not expose a global transform"));
                TransformObject->SetObjectField(ElementKey.Name.ToString(), SampleObject);
                continue;
            }

            const FTransform GlobalTransform = Hierarchy->GetGlobalTransform(ElementKey, false);
            SampleObject->SetObjectField(TEXT("global"), TransformToJsonObject(GlobalTransform));
            TransformObject->SetObjectField(ElementKey.Name.ToString(), SampleObject);
            CaseTransforms.Add(ElementKey.Name.ToString(), GlobalTransform);
        }

        if (!bHasBaseline && CaseTransforms.Num() > 0)
        {
            BaselineTransforms = CaseTransforms;
            BaselineCaseName = ProbeCase.Name;
            bHasBaseline = true;
        }

        TSharedPtr<FJsonObject> DeltaObject = MakeShared<FJsonObject>();
        if (bHasBaseline)
        {
            for (const TPair<FString, FTransform>& Pair : CaseTransforms)
            {
                const FTransform* BaselineTransform = BaselineTransforms.Find(Pair.Key);
                if (!BaselineTransform)
                {
                    continue;
                }

                const FVector Delta = Pair.Value.GetLocation() - BaselineTransform->GetLocation();
                TSharedPtr<FJsonObject> ElementDeltaObject = MakeShared<FJsonObject>();
                ElementDeltaObject->SetArrayField(TEXT("delta"), VectorToJsonArray(Delta));
                ElementDeltaObject->SetNumberField(TEXT("distance"), Delta.Size());
                DeltaObject->SetObjectField(Pair.Key, ElementDeltaObject);
            }
        }

        CaseObject->SetObjectField(TEXT("property_inputs"), PropertyInputsObject);
        CaseObject->SetObjectField(TEXT("property_echo"), PropertyEchoObject);
        CaseObject->SetObjectField(TEXT("curve_inputs"), CurveInputsObject);
        CaseObject->SetObjectField(TEXT("curve_echo_after_set"), CurveEchoAfterSetObject);
        CaseObject->SetObjectField(TEXT("curve_echo_after_execute"), CurveEchoAfterExecuteObject);
        CaseObject->SetArrayField(TEXT("execute_results"), ExecuteResultValues);
        CaseObject->SetObjectField(TEXT("transforms"), TransformObject);
        CaseObject->SetObjectField(TEXT("delta_from_baseline"), DeltaObject);
        CaseObject->SetArrayField(TEXT("errors"), CaseErrorValues);
        CaseObject->SetArrayField(TEXT("warnings"), CaseWarningValues);
        CaseObject->SetBoolField(TEXT("success"), CaseErrorValues.Num() == 0);
        CaseValues.Add(MakeShared<FJsonValueObject>(CaseObject));
    }

    TArray<TSharedPtr<FJsonValue>> SampleElementValues;
    for (const FString& SampleElement : SampleElements)
    {
        SampleElementValues.Add(MakeShared<FJsonValueString>(SampleElement));
    }

    TArray<TSharedPtr<FJsonValue>> ExecuteEventValues;
    for (const FString& ExecuteEvent : ExecuteEvents)
    {
        ExecuteEventValues.Add(MakeShared<FJsonValueString>(ExecuteEvent));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetBoolField(TEXT("read_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetStringField(TEXT("control_rig_asset"), ResolvedAssetPath);
    ResultObj->SetStringField(TEXT("control_rig_class"), ResolvedClassPath);
    ResultObj->SetStringField(TEXT("baseline_case"), BaselineCaseName);
    ResultObj->SetStringField(TEXT("should_trace_property"), ShouldTracePropertyName);
    ResultObj->SetStringField(TEXT("interaction_location_property"), InteractionLocationPropertyName);
    ResultObj->SetArrayField(TEXT("sample_elements"), SampleElementValues);
    ResultObj->SetArrayField(TEXT("execute_events"), ExecuteEventValues);
    ResultObj->SetNumberField(TEXT("case_count"), CaseValues.Num());
    ResultObj->SetArrayField(TEXT("cases"), CaseValues);
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSampleControlRigPrePostRuntimePose(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    const FString ShouldTracePropertyName = GetStringParam(Params, TEXT("should_trace_property"), TEXT("ShouldDoIKTrace"));
    const FString InteractionLocationPropertyName = GetStringParam(Params, TEXT("interaction_location_property"), TEXT("InteractionWorldLocation"));
    const TArray<FControlRigDirectProbeCase> ProbeCases = ParseControlRigPrePostCases(Params, ShouldTracePropertyName, InteractionLocationPropertyName);

    const TArray<FString> DefaultSampleElements = {
        TEXT("pelvis"),
        TEXT("thigh_l"),
        TEXT("calf_l"),
        TEXT("foot_l"),
        TEXT("thigh_r"),
        TEXT("calf_r"),
        TEXT("foot_r"),
        TEXT("IK_foot_L"),
        TEXT("IK_foot_R"),
        TEXT("head_ctrl")
    };
    const TArray<FString> SampleElements = GetStringArrayParam(Params, TEXT("sample_elements"), DefaultSampleElements);

    const TArray<FString> DefaultExecuteEvents = {
        TEXT("Forwards Solve")
    };
    const TArray<FString> ExecuteEvents = GetStringArrayParam(Params, TEXT("execute_events"), DefaultExecuteEvents);

    TArray<TSharedPtr<FJsonValue>> CaseValues;
    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;
    FString ResolvedAssetPath;
    FString ResolvedClassPath;

    for (const FControlRigDirectProbeCase& ProbeCase : ProbeCases)
    {
        FString CaseAssetPath;
        FString CaseClassPath;
        FString CreateError;
        UControlRig* ControlRig = CreateTransientControlRigFromParams(Params, CaseAssetPath, CaseClassPath, CreateError);
        if (!ControlRig)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(CreateError);
        }

        if (ResolvedAssetPath.IsEmpty())
        {
            ResolvedAssetPath = CaseAssetPath;
        }
        if (ResolvedClassPath.IsEmpty())
        {
            ResolvedClassPath = CaseClassPath;
        }

        TSharedPtr<FJsonObject> CaseObject = MakeShared<FJsonObject>();
        CaseObject->SetStringField(TEXT("name"), ProbeCase.Name);
        CaseObject->SetStringField(TEXT("control_rig_class"), CaseClassPath);

        TArray<TSharedPtr<FJsonValue>> CaseErrorValues;
        TArray<TSharedPtr<FJsonValue>> CaseWarningValues;
        auto AddCaseError = [&CaseErrorValues, &ErrorValues, &ProbeCase](const FString& ErrorText)
        {
            CaseErrorValues.Add(MakeShared<FJsonValueString>(ErrorText));
            ErrorValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%s: %s"), *ProbeCase.Name, *ErrorText)));
        };
        auto AddCaseWarning = [&CaseWarningValues, &WarningValues, &ProbeCase](const FString& WarningText)
        {
            CaseWarningValues.Add(MakeShared<FJsonValueString>(WarningText));
            WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%s: %s"), *ProbeCase.Name, *WarningText)));
        };

        ControlRig->Initialize(true);
        URigHierarchy* Hierarchy = ControlRig->GetHierarchy();
        if (!Hierarchy)
        {
            AddCaseError(TEXT("ControlRig hierarchy is null after Initialize"));
            CaseObject->SetArrayField(TEXT("errors"), CaseErrorValues);
            CaseObject->SetArrayField(TEXT("warnings"), CaseWarningValues);
            CaseValues.Add(MakeShared<FJsonValueObject>(CaseObject));
            continue;
        }

        TSharedPtr<FJsonObject> PropertyInputsObject = MakeShared<FJsonObject>();
        TSharedPtr<FJsonObject> PropertyEchoObject = MakeShared<FJsonObject>();
        for (const TPair<FString, TSharedPtr<FJsonValue>>& Pair : ProbeCase.PropertyValues)
        {
            PropertyInputsObject->SetField(Pair.Key, Pair.Value);
            FString PropertyError;
            if (!SetUObjectPropertyFromJson(ControlRig, Pair.Key, Pair.Value, PropertyError))
            {
                AddCaseError(PropertyError);
                continue;
            }
            PropertyEchoObject->SetField(Pair.Key, GetUObjectPropertyJson(ControlRig, Pair.Key));
        }

        TSharedPtr<FJsonObject> CurveInputsObject = MakeShared<FJsonObject>();
        TSharedPtr<FJsonObject> CurveEchoBeforeExecuteObject = MakeShared<FJsonObject>();
        for (const TPair<FName, double>& Pair : ProbeCase.CurveValues)
        {
            CurveInputsObject->SetNumberField(Pair.Key.ToString(), Pair.Value);
            const FRigElementKey CurveKey(Pair.Key, ERigElementType::Curve);
            if (!Hierarchy->Contains(CurveKey))
            {
                AddCaseError(FString::Printf(TEXT("Curve '%s' not found in ControlRig hierarchy"), *Pair.Key.ToString()));
                continue;
            }

            Hierarchy->SetCurveValue(CurveKey, static_cast<float>(Pair.Value), false);
            CurveEchoBeforeExecuteObject->SetNumberField(Pair.Key.ToString(), Hierarchy->GetCurveValue(CurveKey));
        }

        TMap<FString, FTransform> PreTransforms;
        TSharedPtr<FJsonObject> PrePoseObject = SampleRigElementsToJson(Hierarchy, SampleElements, PreTransforms);

        TArray<TSharedPtr<FJsonValue>> ExecuteResultValues;
        for (const FString& EventName : ExecuteEvents)
        {
            TSharedPtr<FJsonObject> ExecuteObject = MakeShared<FJsonObject>();
            ExecuteObject->SetStringField(TEXT("event"), EventName);
            const bool bExecuted = ControlRig->Execute(FName(*EventName));
            ExecuteObject->SetBoolField(TEXT("success"), bExecuted);
            ExecuteResultValues.Add(MakeShared<FJsonValueObject>(ExecuteObject));
            if (!bExecuted)
            {
                const FString WarningText = FString::Printf(TEXT("ControlRig Execute returned false for event '%s'"), *EventName);
                ExecuteObject->SetStringField(TEXT("warning"), WarningText);
                AddCaseWarning(WarningText);
            }
        }

        TMap<FString, FTransform> PostTransforms;
        TSharedPtr<FJsonObject> PostPoseObject = SampleRigElementsToJson(Hierarchy, SampleElements, PostTransforms);
        TSharedPtr<FJsonObject> DeltaObject = BuildRigPoseDeltaObject(PreTransforms, PostTransforms);

        TSharedPtr<FJsonObject> CurveEchoAfterExecuteObject = MakeShared<FJsonObject>();
        for (const TPair<FName, double>& Pair : ProbeCase.CurveValues)
        {
            const FRigElementKey CurveKey(Pair.Key, ERigElementType::Curve);
            if (Hierarchy->Contains(CurveKey))
            {
                CurveEchoAfterExecuteObject->SetNumberField(Pair.Key.ToString(), Hierarchy->GetCurveValue(CurveKey));
            }
        }

        CaseObject->SetObjectField(TEXT("property_inputs"), PropertyInputsObject);
        CaseObject->SetObjectField(TEXT("property_echo"), PropertyEchoObject);
        CaseObject->SetObjectField(TEXT("curve_inputs"), CurveInputsObject);
        CaseObject->SetObjectField(TEXT("curve_echo_before_execute"), CurveEchoBeforeExecuteObject);
        CaseObject->SetArrayField(TEXT("execute_results"), ExecuteResultValues);
        CaseObject->SetObjectField(TEXT("pre_pose"), PrePoseObject);
        CaseObject->SetObjectField(TEXT("post_pose"), PostPoseObject);
        CaseObject->SetObjectField(TEXT("deltas"), DeltaObject);
        CaseObject->SetObjectField(TEXT("curve_echo_after_execute"), CurveEchoAfterExecuteObject);
        CaseObject->SetArrayField(TEXT("errors"), CaseErrorValues);
        CaseObject->SetArrayField(TEXT("warnings"), CaseWarningValues);
        CaseObject->SetBoolField(TEXT("success"), CaseErrorValues.Num() == 0);
        CaseValues.Add(MakeShared<FJsonValueObject>(CaseObject));
    }

    TArray<TSharedPtr<FJsonValue>> SampleElementValues;
    for (const FString& SampleElement : SampleElements)
    {
        SampleElementValues.Add(MakeShared<FJsonValueString>(SampleElement));
    }

    TArray<TSharedPtr<FJsonValue>> ExecuteEventValues;
    for (const FString& ExecuteEvent : ExecuteEvents)
    {
        ExecuteEventValues.Add(MakeShared<FJsonValueString>(ExecuteEvent));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetBoolField(TEXT("read_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
    ResultObj->SetBoolField(TEXT("same_instance_prepost"), true);
    ResultObj->SetStringField(TEXT("runtime_source"), TEXT("direct_transient_controlrig"));
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Samples a transient ControlRig hierarchy before and after execute events. It does not instrument the compiled AnimGraph node stack."));
    ResultObj->SetStringField(TEXT("control_rig_asset"), ResolvedAssetPath);
    ResultObj->SetStringField(TEXT("control_rig_class"), ResolvedClassPath);
    ResultObj->SetStringField(TEXT("should_trace_property"), ShouldTracePropertyName);
    ResultObj->SetStringField(TEXT("interaction_location_property"), InteractionLocationPropertyName);
    ResultObj->SetArrayField(TEXT("sample_elements"), SampleElementValues);
    ResultObj->SetArrayField(TEXT("execute_events"), ExecuteEventValues);
    ResultObj->SetNumberField(TEXT("case_count"), CaseValues.Num());
    ResultObj->SetArrayField(TEXT("cases"), CaseValues);
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSampleAnimNodePrePostRuntimePose(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    const bool bDryRun = GetBoolParam(Params, TEXT("dry_run"), true);

    FString BlueprintName = GetStringParam(Params, TEXT("blueprint_name"));
    if (BlueprintName.IsEmpty())
    {
        BlueprintName = GetStringParam(Params, TEXT("anim_blueprint"));
    }
    if (BlueprintName.IsEmpty())
    {
        BlueprintName = GetStringParam(Params, TEXT("anim_blueprint_path"));
    }
    if (BlueprintName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' or 'anim_blueprint' parameter"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    TSharedPtr<FJsonObject> ResolveParams = MakeShared<FJsonObject>();
    ResolveParams->Values = Params->Values;
    const bool bHasGraphSelector =
        ResolveParams->HasField(TEXT("graph_id")) ||
        ResolveParams->HasField(TEXT("graph_name")) ||
        ResolveParams->HasField(TEXT("graph_type"));
    if (!bHasGraphSelector)
    {
        ResolveParams->SetStringField(TEXT("graph_name"), TEXT("AnimGraph"));
        ResolveParams->SetStringField(TEXT("graph_type"), TEXT("function"));
    }

    bool bCreated = false;
    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraph(Blueprint, ResolveParams, false, bCreated, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    const FString NodeId = GetStringParam(Params, TEXT("node_id"));
    const FString NodeType = GetStringParam(Params, TEXT("node_type"));
    const FString TitleContains = GetStringParam(Params, TEXT("title_contains"));
    const bool bIncludePins = GetBoolParam(Params, TEXT("include_pins"), true);
    const int32 MaxDepth = GetClampedIntParam(Params, TEXT("max_depth"), 3, 1, 8);

    TArray<UAnimGraphNode_Base*> Candidates;
    TArray<TSharedPtr<FJsonValue>> CandidateValues;
    bool bNodeIdMatchedNonAnimNode = false;
    for (UEdGraphNode* Node : TargetGraph->Nodes)
    {
        if (!Node)
        {
            continue;
        }

        const bool bMatchesNodeId = NodeId.IsEmpty() || Node->NodeGuid.ToString().Equals(NodeId, ESearchCase::IgnoreCase);
        if (!bMatchesNodeId)
        {
            continue;
        }

        UAnimGraphNode_Base* AnimGraphNode = Cast<UAnimGraphNode_Base>(Node);
        if (!AnimGraphNode)
        {
            if (!NodeId.IsEmpty())
            {
                bNodeIdMatchedNonAnimNode = true;
            }
            continue;
        }

        if (!MatchesNodeFilter(Node, NodeType, TitleContains))
        {
            continue;
        }

        Candidates.Add(AnimGraphNode);

        TSharedPtr<FJsonObject> CandidateObject = NodeToJson(AnimGraphNode, false);
        CandidateObject->SetStringField(TEXT("mvp_kind"), GetAnimNodePrePostMVPKind(AnimGraphNode));
        CandidateObject->SetBoolField(TEXT("isolated_sampler_mvp_supported"), Cast<UAnimGraphNode_RigidBody>(AnimGraphNode) || Cast<UAnimGraphNode_Trail>(AnimGraphNode));
        CandidateValues.Add(MakeShared<FJsonValueObject>(CandidateObject));
    }

    if (Candidates.Num() != 1)
    {
        FString ErrorText;
        if (bNodeIdMatchedNonAnimNode)
        {
            ErrorText = FString::Printf(TEXT("node_id '%s' matched a non-AnimGraph node"), *NodeId);
        }
        else if (Candidates.Num() == 0)
        {
            ErrorText = FString::Printf(TEXT("No AnimGraph node matched node_id='%s', node_type='%s', title_contains='%s'"), *NodeId, *NodeType, *TitleContains);
        }
        else
        {
            ErrorText = FString::Printf(TEXT("Ambiguous AnimGraph node selector matched %d nodes; provide node_id"), Candidates.Num());
        }

        TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(ErrorText);
        ErrorObj->SetStringField(TEXT("blueprint_name"), BlueprintName);
        ErrorObj->SetStringField(TEXT("blueprint_path"), Blueprint->GetPathName());
        AddGraphField(ErrorObj, Blueprint, TargetGraph);
        ErrorObj->SetArrayField(TEXT("candidates"), CandidateValues);
        return ErrorObj;
    }

    UAnimGraphNode_Base* TargetNode = Candidates[0];
    UEdGraphPin* InputPosePin = FindPreferredInputPosePinForNode(TargetNode);
    UEdGraphPin* OutputPosePin = FindPreferredOutputPosePinForNode(TargetNode);
    const FString MVPKind = GetAnimNodePrePostMVPKind(TargetNode);
    const bool bIsolatedSamplerSupported = Cast<UAnimGraphNode_RigidBody>(TargetNode) || Cast<UAnimGraphNode_Trail>(TargetNode);

    TSharedPtr<FJsonObject> TargetNodeObject = NodeToJson(TargetNode, bIncludePins);
    TargetNodeObject->SetStringField(TEXT("mvp_kind"), MVPKind);
    TargetNodeObject->SetBoolField(TEXT("isolated_sampler_mvp_supported"), bIsolatedSamplerSupported);
    TargetNodeObject->SetStringField(TEXT("support_note"), GetAnimNodePrePostSupportNote(TargetNode));
    TargetNodeObject->SetObjectField(TEXT("settings"), AnimGraphNodeSettingsToJson(TargetNode, MaxDepth));
    TargetNodeObject->SetObjectField(TEXT("preferred_input_pose_pin"), PinToJson(InputPosePin));
    TargetNodeObject->SetObjectField(TEXT("preferred_output_pose_pin"), PinToJson(OutputPosePin));
    TargetNodeObject->SetArrayField(TEXT("upstream_pose_links"), LinkedPinsToJsonValues(InputPosePin));
    TargetNodeObject->SetArrayField(TEXT("downstream_pose_links"), LinkedPinsToJsonValues(OutputPosePin));

    const TArray<FString> SampleBones = GetStringArrayParam(Params, TEXT("sample_bones"), bDryRun ? TArray<FString>() : GetDefaultAnimNodePrePostSampleBones());
    const TArray<FString> SampleSockets = GetStringArrayParam(Params, TEXT("sample_sockets"), TArray<FString>());

    if (!bDryRun)
    {
        return BuildAnimNodePrePostRuntimeTickDeltaResponse(
            Params,
            BlueprintName,
            Blueprint,
            TargetGraph,
            TargetNode,
            TargetNodeObject,
            SampleBones,
            SampleSockets,
            bIsolatedSamplerSupported);
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), true);
    ResultObj->SetBoolField(TEXT("read_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetBoolField(TEXT("runtime_only"), false);
    ResultObj->SetBoolField(TEXT("dry_run"), true);
    ResultObj->SetStringField(TEXT("mode"), TEXT("dry_run_target_resolver"));
    ResultObj->SetBoolField(TEXT("runtime_graph_prepost"), false);
    ResultObj->SetBoolField(TEXT("same_instance_prepost"), false);
    ResultObj->SetBoolField(TEXT("original_assets_modified"), false);
    ResultObj->SetBoolField(TEXT("temp_assets_created"), false);
    ResultObj->SetStringField(TEXT("next_implementation_mode"), TEXT("isolated_temp_components"));
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Phase 1 resolves one AnimGraph node and reports feasibility only. It does not tick components or sample poses."));
    ResultObj->SetStringField(TEXT("blueprint_name"), BlueprintName);
    ResultObj->SetStringField(TEXT("blueprint_path"), Blueprint->GetPathName());
    ResultObj->SetNumberField(TEXT("max_depth"), MaxDepth);
    ResultObj->SetObjectField(TEXT("target_node"), TargetNodeObject);
    ResultObj->SetArrayField(TEXT("requested_sample_bones"), StringArrayToJsonValues(SampleBones));
    ResultObj->SetArrayField(TEXT("requested_sample_sockets"), StringArrayToJsonValues(SampleSockets));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSampleSkeletalBonesInSIE(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    const FString ActorLabel = GetStringParam(Params, TEXT("actor_label"), FString());
    const FString ActorName = GetStringParam(Params, TEXT("actor_name"), FString());
    const FString ActorPath = GetStringParam(Params, TEXT("actor_path"), FString());
    const FString ComponentName = GetStringParam(Params, TEXT("component_name"), FString());

    bool bPreferPIEWorld = true;
    Params->TryGetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    const bool bRequirePIEWorld = GetBoolParam(Params, TEXT("require_pie_world"), false);

    const TArray<FString> DefaultBones = {
        TEXT("root"),
        TEXT("pelvis"),
        TEXT("spine_03"),
        TEXT("head"),
        TEXT("foot_l"),
        TEXT("foot_r")
    };
    const TArray<FString> Bones = GetStringArrayParam(Params, TEXT("bones"), DefaultBones);
    const TArray<FString> Sockets = GetStringArrayParam(Params, TEXT("sockets"), TArray<FString>());

    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;

    const TArray<UWorld*> CandidateWorlds = GetCandidateWorldsForSkeletalSampling(bPreferPIEWorld, !bRequirePIEWorld);
    AActor* MatchedActor = nullptr;
    USkeletalMeshComponent* MatchedComponent = nullptr;
    UWorld* MatchedWorld = nullptr;
    int32 MatchedActorCount = 0;
    int32 MatchedComponentCount = 0;

    for (UWorld* World : CandidateWorlds)
    {
        const TArray<AActor*> Actors = FindSkeletalSamplerActors(World, ActorLabel, ActorName, ActorPath);
        if (Actors.Num() == 0)
        {
            continue;
        }

        MatchedActorCount += Actors.Num();

        for (AActor* Actor : Actors)
        {
            int32 CandidateComponentCount = 0;
            USkeletalMeshComponent* Component = FindSkeletalSamplerComponent(Actor, ComponentName, CandidateComponentCount);
            if (!Component)
            {
                continue;
            }

            MatchedActor = Actor;
            MatchedComponent = Component;
            MatchedWorld = World;
            MatchedComponentCount = CandidateComponentCount;
            break;
        }

        if (MatchedActor && MatchedComponent)
        {
            break;
        }
    }

    if (!MatchedActor || !MatchedComponent || !MatchedWorld)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(bRequirePIEWorld
            ? FString::Printf(
                TEXT("No SkeletalMeshComponent actor matched actor_label='%s', actor_name='%s', actor_path='%s', component_name='%s' in active PIE/SIE/play worlds"),
                *ActorLabel,
                *ActorName,
                *ActorPath,
                *ComponentName)
            : FString::Printf(
                TEXT("No SkeletalMeshComponent actor matched actor_label='%s', actor_name='%s', actor_path='%s', component_name='%s' in candidate editor/PIE worlds"),
                *ActorLabel,
                *ActorName,
                *ActorPath,
                *ComponentName));
    }

    if (MatchedActorCount > 1)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
            TEXT("Matched %d actors; sampled the first matching actor in world priority order"),
            MatchedActorCount)));
    }

    if (ComponentName.IsEmpty() && MatchedComponentCount > 1)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
            TEXT("Actor has %d SkeletalMeshComponents; sampled the first component because component_name was not provided"),
            MatchedComponentCount)));
    }

    TSharedPtr<FJsonObject> BoneSamplesObject = MakeShared<FJsonObject>();
    for (const FString& BoneName : Bones)
    {
        if (BoneName.IsEmpty())
        {
            continue;
        }

        TSharedPtr<FJsonObject> BoneSample = SampleBoneTransformToJson(MatchedComponent, BoneName);
        if (!BoneSample->GetBoolField(TEXT("valid")))
        {
            FString ErrorText;
            if (BoneSample->TryGetStringField(TEXT("error"), ErrorText))
            {
                WarningValues.Add(MakeShared<FJsonValueString>(ErrorText));
            }
        }
        BoneSamplesObject->SetObjectField(BoneName, BoneSample);
    }

    TSharedPtr<FJsonObject> SocketSamplesObject = MakeShared<FJsonObject>();
    for (const FString& SocketName : Sockets)
    {
        if (SocketName.IsEmpty())
        {
            continue;
        }

        TSharedPtr<FJsonObject> SocketSample = SampleSocketTransformToJson(MatchedComponent, SocketName);
        if (!SocketSample->GetBoolField(TEXT("valid")))
        {
            FString ErrorText;
            if (SocketSample->TryGetStringField(TEXT("error"), ErrorText))
            {
                WarningValues.Add(MakeShared<FJsonValueString>(ErrorText));
            }
        }
        SocketSamplesObject->SetObjectField(SocketName, SocketSample);
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetBoolField(TEXT("read_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetStringField(TEXT("runtime_source"), TEXT("active_skeletal_mesh_component"));
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Samples the current SkeletalMeshComponent pose from an active PIE/SIE/play world when available, otherwise the editor world. It does not start or tick SIE by itself."));
    ResultObj->SetBoolField(TEXT("starts_sie"), false);
    ResultObj->SetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    ResultObj->SetBoolField(TEXT("require_pie_world"), bRequirePIEWorld);
    ResultObj->SetBoolField(TEXT("is_play_session_active"), IsBlueprintNodePlaySessionActive());
    ResultObj->SetStringField(TEXT("sampled_world_type"), BlueprintNodeWorldTypeToString(MatchedWorld));
    ResultObj->SetStringField(TEXT("sampled_world_name"), MatchedWorld ? MatchedWorld->GetName() : FString());
    ResultObj->SetNumberField(TEXT("matched_actor_count"), MatchedActorCount);
    ResultObj->SetNumberField(TEXT("matched_component_count"), MatchedComponentCount);
    ResultObj->SetStringField(TEXT("requested_actor_label"), ActorLabel);
    ResultObj->SetStringField(TEXT("requested_actor_name"), ActorName);
    ResultObj->SetStringField(TEXT("requested_actor_path"), ActorPath);
    ResultObj->SetStringField(TEXT("requested_component_name"), ComponentName);
    ResultObj->SetArrayField(TEXT("requested_bones"), StringArrayToJsonValues(Bones));
    ResultObj->SetArrayField(TEXT("requested_sockets"), StringArrayToJsonValues(Sockets));
    ResultObj->SetObjectField(TEXT("actor"), ActorToSkeletalSamplerJson(MatchedActor));
    ResultObj->SetObjectField(TEXT("component"), SkeletalComponentToSamplerJson(MatchedComponent));
    ResultObj->SetObjectField(TEXT("bone_samples"), BoneSamplesObject);
    ResultObj->SetObjectField(TEXT("socket_samples"), SocketSamplesObject);
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleInspectAnimInstanceRuntimeState(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    const FString ActorLabel = GetStringParam(Params, TEXT("actor_label"), FString());
    const FString ActorName = GetStringParam(Params, TEXT("actor_name"), FString());
    const FString ActorPath = GetStringParam(Params, TEXT("actor_path"), FString());
    const FString ComponentName = GetStringParam(Params, TEXT("component_name"), FString());
    const bool bIncludeMontages = GetBoolParam(Params, TEXT("include_montages"), true);
    const bool bIncludeCurves = GetBoolParam(Params, TEXT("include_curves"), false);

    bool bPreferPIEWorld = true;
    Params->TryGetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    const bool bRequirePIEWorld = GetBoolParam(Params, TEXT("require_pie_world"), false);

    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;

    const TArray<UWorld*> CandidateWorlds = GetCandidateWorldsForSkeletalSampling(bPreferPIEWorld, !bRequirePIEWorld);
    AActor* MatchedActor = nullptr;
    USkeletalMeshComponent* MatchedComponent = nullptr;
    UWorld* MatchedWorld = nullptr;
    int32 MatchedActorCount = 0;
    int32 MatchedComponentCount = 0;

    for (UWorld* World : CandidateWorlds)
    {
        const TArray<AActor*> Actors = FindSkeletalSamplerActors(World, ActorLabel, ActorName, ActorPath);
        if (Actors.Num() == 0)
        {
            continue;
        }

        MatchedActorCount += Actors.Num();

        for (AActor* Actor : Actors)
        {
            int32 CandidateComponentCount = 0;
            USkeletalMeshComponent* Component = FindSkeletalSamplerComponent(Actor, ComponentName, CandidateComponentCount);
            if (!Component)
            {
                continue;
            }

            MatchedActor = Actor;
            MatchedComponent = Component;
            MatchedWorld = World;
            MatchedComponentCount = CandidateComponentCount;
            break;
        }

        if (MatchedActor && MatchedComponent)
        {
            break;
        }
    }

    if (!MatchedActor || !MatchedComponent || !MatchedWorld)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(bRequirePIEWorld
            ? FString::Printf(
                TEXT("No SkeletalMeshComponent actor matched actor_label='%s', actor_name='%s', actor_path='%s', component_name='%s' in active PIE/SIE/play worlds"),
                *ActorLabel,
                *ActorName,
                *ActorPath,
                *ComponentName)
            : FString::Printf(
                TEXT("No SkeletalMeshComponent actor matched actor_label='%s', actor_name='%s', actor_path='%s', component_name='%s' in candidate editor/PIE worlds"),
                *ActorLabel,
                *ActorName,
                *ActorPath,
                *ComponentName));
    }

    if (MatchedActorCount > 1)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
            TEXT("Matched %d actors; inspected the first matching actor in world priority order"),
            MatchedActorCount)));
    }

    if (ComponentName.IsEmpty() && MatchedComponentCount > 1)
    {
        WarningValues.Add(MakeShared<FJsonValueString>(FString::Printf(
            TEXT("Actor has %d SkeletalMeshComponents; inspected the first component because component_name was not provided"),
            MatchedComponentCount)));
    }

    UAnimInstance* AnimInstance = MatchedComponent->GetAnimInstance();
    if (!AnimInstance)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Matched SkeletalMeshComponent '%s' has no AnimInstance. animation_mode=%s anim_class=%s"),
            *MatchedComponent->GetName(),
            *AnimationModeToString(MatchedComponent->GetAnimationMode()),
            MatchedComponent->GetAnimClass() ? *MatchedComponent->GetAnimClass()->GetPathName() : TEXT("<none>")));
    }

    TSharedPtr<FJsonObject> AnimInstanceObject = MakeShared<FJsonObject>();
    AnimInstanceObject->SetStringField(TEXT("name"), AnimInstance->GetName());
    AnimInstanceObject->SetStringField(TEXT("path"), AnimInstance->GetPathName());
    AnimInstanceObject->SetStringField(TEXT("class"), AnimInstance->GetClass() ? AnimInstance->GetClass()->GetPathName() : FString());
    AnimInstanceObject->SetStringField(TEXT("outer"), AnimInstance->GetOuter() ? AnimInstance->GetOuter()->GetPathName() : FString());

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetBoolField(TEXT("read_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetStringField(TEXT("runtime_source"), TEXT("active_anim_instance"));
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Reads runtime state from the current SkeletalMeshComponent AnimInstance in active PIE/SIE/play worlds when available, otherwise editor world. It does not start or tick SIE by itself."));
    ResultObj->SetBoolField(TEXT("starts_sie"), false);
    ResultObj->SetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    ResultObj->SetBoolField(TEXT("require_pie_world"), bRequirePIEWorld);
    ResultObj->SetBoolField(TEXT("is_play_session_active"), IsBlueprintNodePlaySessionActive());
    ResultObj->SetStringField(TEXT("sampled_world_type"), BlueprintNodeWorldTypeToString(MatchedWorld));
    ResultObj->SetStringField(TEXT("sampled_world_name"), MatchedWorld ? MatchedWorld->GetName() : FString());
    ResultObj->SetNumberField(TEXT("matched_actor_count"), MatchedActorCount);
    ResultObj->SetNumberField(TEXT("matched_component_count"), MatchedComponentCount);
    ResultObj->SetStringField(TEXT("requested_actor_label"), ActorLabel);
    ResultObj->SetStringField(TEXT("requested_actor_name"), ActorName);
    ResultObj->SetStringField(TEXT("requested_actor_path"), ActorPath);
    ResultObj->SetStringField(TEXT("requested_component_name"), ComponentName);
    ResultObj->SetObjectField(TEXT("actor"), ActorToSkeletalSamplerJson(MatchedActor));
    ResultObj->SetObjectField(TEXT("component"), SkeletalComponentToSamplerJson(MatchedComponent));
    ResultObj->SetObjectField(TEXT("anim_instance"), AnimInstanceObject);
    ResultObj->SetObjectField(TEXT("state_machines"), AnimStateMachineRuntimeStateToJson(AnimInstance, Params, WarningValues));
    if (bIncludeMontages)
    {
        ResultObj->SetObjectField(TEXT("active_montage"), AnimMontageRuntimeStateToJson(AnimInstance));
    }
    if (bIncludeCurves)
    {
        ResultObj->SetObjectField(TEXT("curves"), AnimCurvesRuntimeStateToJson(AnimInstance, Params, WarningValues));
    }
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSetAnimInstanceRuntimePropertyForProbe(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    bool bPreferPIEWorld = true;
    Params->TryGetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    const bool bRequirePIEWorld = GetBoolParam(Params, TEXT("require_pie_world"), false);

    const bool bIncludePreviousValues = GetBoolParam(Params, TEXT("include_previous_values"), true);
    const bool bIncludeSnapshotAfter = GetBoolParam(Params, TEXT("include_snapshot_after"), true);
    const bool bTickAfterSet = GetBoolParam(Params, TEXT("tick_after_set"), false);
    const int32 TickCount = bTickAfterSet
        ? GetClampedIntParam(Params, TEXT("tick_count"), 1, 0, 240)
        : 0;
    const double TickDeltaTime = GetClampedNumberParam(Params, TEXT("tick_delta_time"), 1.0 / 30.0, 0.0, 1.0);
    const bool bRefreshBoneTransforms = GetBoolParam(Params, TEXT("refresh_bone_transforms"), true);

    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;

    FAnimInstanceRuntimeTarget Target;
    FString TargetError;
    if (!FindAnimInstanceRuntimeTarget(Params, bPreferPIEWorld, bRequirePIEWorld, TEXT("set runtime properties on"), Target, WarningValues, TargetError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TargetError);
    }

    const TArray<FAnimInstanceRuntimePropertyAssignment> Assignments = ParseAnimInstanceRuntimePropertyAssignments(Params);
    if (Assignments.Num() == 0)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("No runtime properties requested. Provide 'properties' as an object/array or 'property_name' plus 'value'."));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("read_only"), false);
    ResultObj->SetBoolField(TEXT("runtime_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetBoolField(TEXT("saves_assets"), false);
    ResultObj->SetStringField(TEXT("runtime_source"), TEXT("active_anim_instance"));
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Sets properties only on the currently matched live AnimInstance object for probing. It does not save or modify Animation Blueprint assets."));
    ResultObj->SetBoolField(TEXT("starts_sie"), false);
    PopulateAnimInstanceRuntimeTargetFields(ResultObj, Target, bPreferPIEWorld, bRequirePIEWorld);

    ResultObj->SetObjectField(TEXT("applied_properties"), ApplyAnimInstanceRuntimePropertyAssignments(
        Target.AnimInstance,
        Assignments,
        bIncludePreviousValues,
        nullptr,
        ErrorValues));

    if (bTickAfterSet)
    {
        ResultObj->SetObjectField(TEXT("tick_after_set"), TickSkeletalComponentForAnimRuntimeProbe(
            Target.Component,
            TickCount,
            TickDeltaTime,
            bRefreshBoneTransforms,
            WarningValues));
    }

    if (bIncludeSnapshotAfter)
    {
        Target.AnimInstance = Target.Component ? Target.Component->GetAnimInstance() : Target.AnimInstance;
        ResultObj->SetObjectField(TEXT("snapshot_after"), CaptureAnimInstanceRuntimeSnapshot(Target.AnimInstance, Params, WarningValues));
    }

    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSampleAnimStateMachineRuntimeResponse(const TSharedPtr<FJsonObject>& Params)
{
    if (!Params.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing params"));
    }

    bool bPreferPIEWorld = true;
    Params->TryGetBoolField(TEXT("prefer_pie_world"), bPreferPIEWorld);
    const bool bRequirePIEWorld = GetBoolParam(Params, TEXT("require_pie_world"), false);

    const int32 DefaultTickCount = GetClampedIntParam(Params, TEXT("tick_count"), 1, 0, 240);
    const double DefaultTickDeltaTime = GetClampedNumberParam(Params, TEXT("tick_delta_time"), 1.0 / 30.0, 0.0, 1.0);
    const bool bRefreshBoneTransforms = GetBoolParam(Params, TEXT("refresh_bone_transforms"), true);
    const bool bRestoreAfterCaseDefault = GetBoolParam(Params, TEXT("restore_after_case"), true);
    const bool bIncludeBaseline = GetBoolParam(Params, TEXT("include_baseline"), true);

    TArray<TSharedPtr<FJsonValue>> ErrorValues;
    TArray<TSharedPtr<FJsonValue>> WarningValues;

    FAnimInstanceRuntimeTarget Target;
    FString TargetError;
    if (!FindAnimInstanceRuntimeTarget(Params, bPreferPIEWorld, bRequirePIEWorld, TEXT("sampled"), Target, WarningValues, TargetError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TargetError);
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("read_only"), false);
    ResultObj->SetBoolField(TEXT("runtime_only"), true);
    ResultObj->SetBoolField(TEXT("asset_modified"), false);
    ResultObj->SetBoolField(TEXT("saves_assets"), false);
    ResultObj->SetStringField(TEXT("runtime_source"), TEXT("active_anim_instance_state_machine_response"));
    ResultObj->SetStringField(TEXT("runtime_note"), TEXT("Applies requested properties to a live AnimInstance, optionally ticks the matched SkeletalMeshComponent, samples state-machine runtime state, and restores successful properties per case by default. It does not save or modify Animation Blueprint assets."));
    ResultObj->SetBoolField(TEXT("starts_sie"), false);
    ResultObj->SetBoolField(TEXT("restores_after_case_default"), bRestoreAfterCaseDefault);
    PopulateAnimInstanceRuntimeTargetFields(ResultObj, Target, bPreferPIEWorld, bRequirePIEWorld);

    if (bIncludeBaseline)
    {
        ResultObj->SetObjectField(TEXT("baseline"), CaptureAnimInstanceRuntimeSnapshot(Target.AnimInstance, Params, WarningValues));
    }

    const TArray<FAnimStateRuntimeResponseCase> Cases = ParseAnimStateRuntimeResponseCases(
        Params,
        DefaultTickCount,
        DefaultTickDeltaTime,
        bRestoreAfterCaseDefault);

    TArray<TSharedPtr<FJsonValue>> CaseValues;
    int32 SuccessfulCaseCount = 0;
    for (int32 CaseIndex = 0; CaseIndex < Cases.Num(); ++CaseIndex)
    {
        const FAnimStateRuntimeResponseCase& RuntimeCase = Cases[CaseIndex];
        TArray<TSharedPtr<FJsonValue>> CaseErrorValues;
        TArray<TSharedPtr<FJsonValue>> CaseWarningValues;
        TArray<FAnimInstanceRuntimePropertyAssignment> RestoreAssignments;

        TSharedPtr<FJsonObject> CaseObject = MakeShared<FJsonObject>();
        CaseObject->SetStringField(TEXT("name"), RuntimeCase.Name);
        CaseObject->SetNumberField(TEXT("case_index"), CaseIndex);
        CaseObject->SetBoolField(TEXT("restore_after_case"), RuntimeCase.bRestoreAfterCase);
        CaseObject->SetNumberField(TEXT("tick_count"), RuntimeCase.TickCount);
        CaseObject->SetNumberField(TEXT("tick_delta_time"), RuntimeCase.TickDeltaTime);

        CaseObject->SetObjectField(TEXT("applied_properties"), ApplyAnimInstanceRuntimePropertyAssignments(
            Target.AnimInstance,
            RuntimeCase.Assignments,
            true,
            RuntimeCase.bRestoreAfterCase ? &RestoreAssignments : nullptr,
            CaseErrorValues));

        CaseObject->SetObjectField(TEXT("tick"), TickSkeletalComponentForAnimRuntimeProbe(
            Target.Component,
            RuntimeCase.TickCount,
            RuntimeCase.TickDeltaTime,
            bRefreshBoneTransforms,
            CaseWarningValues));

        Target.AnimInstance = Target.Component ? Target.Component->GetAnimInstance() : Target.AnimInstance;
        CaseObject->SetObjectField(TEXT("snapshot"), CaptureAnimInstanceRuntimeSnapshot(Target.AnimInstance, Params, CaseWarningValues));

        if (RuntimeCase.bRestoreAfterCase && RestoreAssignments.Num() > 0)
        {
            TArray<TSharedPtr<FJsonValue>> RestoreErrorValues;
            CaseObject->SetObjectField(TEXT("restore"), ApplyAnimInstanceRuntimePropertyAssignments(
                Target.AnimInstance,
                RestoreAssignments,
                false,
                nullptr,
                RestoreErrorValues));

            for (const TSharedPtr<FJsonValue>& RestoreError : RestoreErrorValues)
            {
                CaseErrorValues.Add(RestoreError);
            }
        }

        const bool bCaseSuccess = CaseErrorValues.Num() == 0;
        CaseObject->SetBoolField(TEXT("success"), bCaseSuccess);
        CaseObject->SetArrayField(TEXT("errors"), CaseErrorValues);
        CaseObject->SetArrayField(TEXT("warnings"), CaseWarningValues);
        if (bCaseSuccess)
        {
            ++SuccessfulCaseCount;
        }
        else
        {
            ErrorValues.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("Case '%s' failed"), *RuntimeCase.Name)));
        }

        CaseValues.Add(MakeShared<FJsonValueObject>(CaseObject));
    }

    ResultObj->SetNumberField(TEXT("case_count"), Cases.Num());
    ResultObj->SetNumberField(TEXT("successful_case_count"), SuccessfulCaseCount);
    ResultObj->SetArrayField(TEXT("cases"), CaseValues);
    ResultObj->SetBoolField(TEXT("success"), ErrorValues.Num() == 0);
    ResultObj->SetArrayField(TEXT("errors"), ErrorValues);
    ResultObj->SetArrayField(TEXT("warnings"), WarningValues);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSetAnimGraphRigidBodySettings(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    bool bAllowNonSample = false;
    Params->TryGetBoolField(TEXT("allow_non_sample"), bAllowNonSample);
    if (!bAllowNonSample && !Blueprint->GetPathName().StartsWith(TEXT("/Game/_MCP_Sample/")))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Refusing to modify non-sample Anim Blueprint '%s'. Pass allow_non_sample=true only for intentional non-sample edits."),
            *Blueprint->GetPathName()));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    FString NodeId;
    Params->TryGetStringField(TEXT("node_id"), NodeId);

    UAnimGraphNode_RigidBody* RigidBodyNode = nullptr;
    for (UEdGraphNode* Node : TargetGraph->Nodes)
    {
        UAnimGraphNode_RigidBody* Candidate = Cast<UAnimGraphNode_RigidBody>(Node);
        if (!Candidate)
        {
            continue;
        }
        if (!NodeId.IsEmpty() && Candidate->NodeGuid.ToString() != NodeId)
        {
            continue;
        }
        RigidBodyNode = Candidate;
        break;
    }

    if (!RigidBodyNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(NodeId.IsEmpty()
            ? TEXT("RigidBody AnimGraph node not found")
            : FString::Printf(TEXT("RigidBody AnimGraph node not found for node_id '%s'"), *NodeId));
    }

    bool bSettingsChanged = false;
    TArray<FString> ChangedFields;

    if (Params->HasField(TEXT("alpha")))
    {
        const double Alpha = Params->GetNumberField(TEXT("alpha"));
        if (!FMath::IsNearlyEqual(RigidBodyNode->Node.Alpha, static_cast<float>(Alpha), KINDA_SMALL_NUMBER))
        {
            RigidBodyNode->Node.Alpha = static_cast<float>(Alpha);
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("Alpha"));
        }
        if (UEdGraphPin* AlphaPin = FUnrealMCPCommonUtils::FindPin(RigidBodyNode, TEXT("Alpha"), EGPD_Input))
        {
            const FString AlphaDefault = FString::Printf(TEXT("%f"), Alpha);
            if (!AlphaPin->DefaultValue.Equals(AlphaDefault, ESearchCase::CaseSensitive))
            {
                if (TargetGraph->GetSchema())
                {
                    TargetGraph->GetSchema()->TrySetDefaultValue(*AlphaPin, AlphaDefault);
                }
                RigidBodyNode->PinDefaultValueChanged(AlphaPin);
                bSettingsChanged = true;
                ChangedFields.Add(TEXT("AlphaPin"));
            }
        }
    }

    if (Params->HasField(TEXT("external_force")))
    {
        const FVector ExternalForce = FUnrealMCPCommonUtils::GetVectorFromJson(Params, TEXT("external_force"));
        if (!RigidBodyNode->Node.ExternalForce.Equals(ExternalForce, KINDA_SMALL_NUMBER))
        {
            RigidBodyNode->Node.ExternalForce = ExternalForce;
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("ExternalForce"));
        }
        if (UEdGraphPin* ExternalForcePin = FUnrealMCPCommonUtils::FindPin(RigidBodyNode, TEXT("ExternalForce"), EGPD_Input))
        {
            const FString ExternalForceDefault = FString::Printf(TEXT("%f,%f,%f"), ExternalForce.X, ExternalForce.Y, ExternalForce.Z);
            if (!ExternalForcePin->DefaultValue.Equals(ExternalForceDefault, ESearchCase::CaseSensitive))
            {
                if (TargetGraph->GetSchema())
                {
                    TargetGraph->GetSchema()->TrySetDefaultValue(*ExternalForcePin, ExternalForceDefault);
                }
                RigidBodyNode->PinDefaultValueChanged(ExternalForcePin);
                bSettingsChanged = true;
                ChangedFields.Add(TEXT("ExternalForcePin"));
            }
        }
    }

    FString SimulationSpaceText;
    if (Params->TryGetStringField(TEXT("simulation_space"), SimulationSpaceText) && !SimulationSpaceText.TrimStartAndEnd().IsEmpty())
    {
        ESimulationSpace SimulationSpace;
        if (!ParseRigidBodySimulationSpace(SimulationSpaceText, SimulationSpace))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("Unsupported simulation_space '%s'. Use ComponentSpace, WorldSpace, or BaseBoneSpace."),
                *SimulationSpaceText));
        }
        if (RigidBodyNode->Node.SimulationSpace != SimulationSpace)
        {
            RigidBodyNode->Node.SimulationSpace = SimulationSpace;
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("SimulationSpace"));
        }
    }

    if (Params->HasField(TEXT("enable_world_geometry")))
    {
        const bool bEnableWorldGeometry = Params->GetBoolField(TEXT("enable_world_geometry"));
        if (RigidBodyNode->Node.bEnableWorldGeometry != bEnableWorldGeometry)
        {
            RigidBodyNode->Node.bEnableWorldGeometry = bEnableWorldGeometry;
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("bEnableWorldGeometry"));
        }
    }

    if (bSettingsChanged)
    {
        FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        RigidBodyNode->ReconstructNode();
        TargetGraph->NotifyGraphChanged();
    }

    TArray<TSharedPtr<FJsonValue>> ChangedFieldValues;
    for (const FString& FieldName : ChangedFields)
    {
        ChangedFieldValues.Add(MakeShared<FJsonValueString>(FieldName));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("settings_changed"), bSettingsChanged);
    ResultObj->SetStringField(TEXT("blueprint"), Blueprint->GetPathName());
    ResultObj->SetStringField(TEXT("graph_name"), TargetGraph->GetName());
    ResultObj->SetStringField(TEXT("node_id"), RigidBodyNode->NodeGuid.ToString());
    ResultObj->SetStringField(TEXT("simulation_space"), GetRigidBodySimulationSpaceName(RigidBodyNode->Node.SimulationSpace));
    ResultObj->SetNumberField(TEXT("alpha"), RigidBodyNode->Node.Alpha);
    ResultObj->SetStringField(TEXT("external_force"), RigidBodyNode->Node.ExternalForce.ToString());
    ResultObj->SetBoolField(TEXT("enable_world_geometry"), RigidBodyNode->Node.bEnableWorldGeometry);
    ResultObj->SetArrayField(TEXT("changed_fields"), ChangedFieldValues);
    ResultObj->SetObjectField(TEXT("rigidbody_node"), NodeToJson(RigidBodyNode, true));
    ResultObj->SetObjectField(TEXT("settings"), AnimGraphNodeSettingsToJson(RigidBodyNode, 4));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleEnsureAnimGraphInputPosePassthrough(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    UAnimGraphNode_Root* RootNode = FindFirstNodeOfType<UAnimGraphNode_Root>(TargetGraph);
    if (!RootNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("AnimGraph root node not found in graph: %s"), *TargetGraph->GetName()));
    }

    bool bCreatedInputNode = false;
    UAnimGraphNode_LinkedInputPose* InputPoseNode = FindFirstNodeOfType<UAnimGraphNode_LinkedInputPose>(TargetGraph);
    if (!InputPoseNode)
    {
        FVector2D NodePosition(-320.0f, 0.0f);
        if (Params->HasField(TEXT("input_node_position")))
        {
            NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("input_node_position"));
        }
        else if (Params->HasField(TEXT("node_position")))
        {
            NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
        }

        InputPoseNode = AddAnimGraphNodeToGraph<UAnimGraphNode_LinkedInputPose>(TargetGraph, NodePosition);
        if (!InputPoseNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create LinkedInputPose node"));
        }
        bCreatedInputNode = true;
    }

    UEdGraphPin* SourcePin = FindFirstPosePin(InputPoseNode, EGPD_Output);
    if (!SourcePin)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("LinkedInputPose output pose pin not found"));
    }

    UEdGraphPin* TargetPin = FindFirstPosePin(RootNode, EGPD_Input, { TEXT("Result") });
    if (!TargetPin)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("AnimGraph root input pose pin not found"));
    }

    const bool bAlreadyConnected = TargetPin->LinkedTo.Contains(SourcePin);
    bool bReplacedExistingLinks = false;
    bool bReplaceExisting = false;
    if (Params->HasField(TEXT("replace_existing")))
    {
        bReplaceExisting = Params->GetBoolField(TEXT("replace_existing"));
    }

    if (!bAlreadyConnected && TargetPin->LinkedTo.Num() > 0)
    {
        if (!bReplaceExisting)
        {
            TArray<TSharedPtr<FJsonValue>> ExistingLinks;
            for (UEdGraphPin* LinkedPin : TargetPin->LinkedTo)
            {
                ExistingLinks.Add(MakeShared<FJsonValueObject>(PinToJson(LinkedPin)));
            }

            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("AnimGraph root pose pin already has a different link; pass replace_existing=true to replace it"));
            ErrorObj->SetObjectField(TEXT("target_pin"), PinToJson(TargetPin));
            ErrorObj->SetArrayField(TEXT("existing_links"), ExistingLinks);
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        TargetPin->BreakAllPinLinks();
        bReplacedExistingLinks = true;
    }

    FPinConnectionResponse ConnectionResponse(CONNECT_RESPONSE_MAKE, FText::GetEmpty());
    bool bConnected = bAlreadyConnected;
    if (!bAlreadyConnected)
    {
        const UEdGraphSchema* GraphSchema = TargetGraph->GetSchema();
        if (!GraphSchema)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get AnimationGraph schema"));
        }

        ConnectionResponse = GraphSchema->CanCreateConnection(SourcePin, TargetPin);
        if (!ConnectionResponse.CanSafeConnect())
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(ConnectionResponse.Message.ToString());
            ErrorObj->SetStringField(TEXT("schema_response"), GetConnectionResponseName(ConnectionResponse.Response));
            ErrorObj->SetStringField(TEXT("schema_message"), ConnectionResponse.Message.ToString());
            ErrorObj->SetObjectField(TEXT("source_pin"), PinToJson(SourcePin));
            ErrorObj->SetObjectField(TEXT("target_pin"), PinToJson(TargetPin));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        if (!GraphSchema->TryCreateConnection(SourcePin, TargetPin))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("AnimationGraph schema failed to create LinkedInputPose -> Root connection"));
        }

        bConnected = true;
    }

    const bool bGraphChanged = bCreatedInputNode || !bAlreadyConnected || bReplacedExistingLinks;
    if (bGraphChanged)
    {
        FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        TargetGraph->NotifyGraphChanged();
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("connected"), bConnected);
    ResultObj->SetBoolField(TEXT("already_connected"), bAlreadyConnected);
    ResultObj->SetBoolField(TEXT("created_input_node"), bCreatedInputNode);
    ResultObj->SetBoolField(TEXT("graph_changed"), bGraphChanged);
    ResultObj->SetBoolField(TEXT("replaced_existing_links"), bReplacedExistingLinks);
    ResultObj->SetStringField(TEXT("schema_response"), GetConnectionResponseName(ConnectionResponse.Response));
    ResultObj->SetStringField(TEXT("schema_message"), ConnectionResponse.Message.ToString());
    ResultObj->SetObjectField(TEXT("input_pose_node"), NodeToJson(InputPoseNode, true));
    ResultObj->SetObjectField(TEXT("root_node"), NodeToJson(RootNode, true));
    ResultObj->SetObjectField(TEXT("source_pin"), PinToJson(SourcePin));
    ResultObj->SetObjectField(TEXT("target_pin"), PinToJson(TargetPin));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleEnsureAnimGraphModifyBoneDemo(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString BoneName;
    if (!Params->TryGetStringField(TEXT("bone_name"), BoneName))
    {
        BoneName = TEXT("head");
    }
    BoneName.TrimStartAndEndInline();
    if (BoneName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'bone_name' cannot be empty"));
    }
    const FName TargetBoneName(*BoneName);

    FVector RotationVector(0.0f, 0.0f, 6.0f);
    if (Params->HasField(TEXT("rotation")))
    {
        RotationVector = FUnrealMCPCommonUtils::GetVectorFromJson(Params, TEXT("rotation"));
    }
    const FRotator AdditiveRotation(RotationVector.X, RotationVector.Y, RotationVector.Z);

    bool bReplaceExisting = false;
    if (Params->HasField(TEXT("replace_existing")))
    {
        bReplaceExisting = Params->GetBoolField(TEXT("replace_existing"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    UAnimGraphNode_Root* RootNode = FindFirstNodeOfType<UAnimGraphNode_Root>(TargetGraph);
    if (!RootNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("AnimGraph root node not found in graph: %s"), *TargetGraph->GetName()));
    }

    bool bCreatedInputNode = false;
    UAnimGraphNode_LinkedInputPose* InputPoseNode = FindFirstNodeOfType<UAnimGraphNode_LinkedInputPose>(TargetGraph);
    if (!InputPoseNode)
    {
        InputPoseNode = AddAnimGraphNodeToGraph<UAnimGraphNode_LinkedInputPose>(TargetGraph, FVector2D(-720.0f, 0.0f));
        if (!InputPoseNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create LinkedInputPose node"));
        }
        bCreatedInputNode = true;
    }

    bool bCreatedLocalToComponentNode = false;
    UAnimGraphNode_LocalToComponentSpace* LocalToComponentNode = FindFirstNodeOfType<UAnimGraphNode_LocalToComponentSpace>(TargetGraph);
    if (!LocalToComponentNode)
    {
        LocalToComponentNode = AddAnimGraphNodeToGraph<UAnimGraphNode_LocalToComponentSpace>(TargetGraph, FVector2D(-480.0f, 0.0f));
        if (!LocalToComponentNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create LocalToComponentSpace node"));
        }
        bCreatedLocalToComponentNode = true;
    }

    bool bCreatedModifyBoneNode = false;
    UAnimGraphNode_ModifyBone* ModifyBoneNode = nullptr;
    for (UEdGraphNode* Node : TargetGraph->Nodes)
    {
        UAnimGraphNode_ModifyBone* Candidate = Cast<UAnimGraphNode_ModifyBone>(Node);
        if (Candidate && Candidate->Node.BoneToModify.BoneName == TargetBoneName)
        {
            ModifyBoneNode = Candidate;
            break;
        }
    }
    if (!ModifyBoneNode)
    {
        ModifyBoneNode = FindFirstNodeOfType<UAnimGraphNode_ModifyBone>(TargetGraph);
    }
    if (!ModifyBoneNode)
    {
        ModifyBoneNode = AddAnimGraphNodeToGraph<UAnimGraphNode_ModifyBone>(TargetGraph, FVector2D(-240.0f, 0.0f));
        if (!ModifyBoneNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create ModifyBone node"));
        }
        bCreatedModifyBoneNode = true;
    }

    bool bCreatedComponentToLocalNode = false;
    UAnimGraphNode_ComponentToLocalSpace* ComponentToLocalNode = FindFirstNodeOfType<UAnimGraphNode_ComponentToLocalSpace>(TargetGraph);
    if (!ComponentToLocalNode)
    {
        ComponentToLocalNode = AddAnimGraphNodeToGraph<UAnimGraphNode_ComponentToLocalSpace>(TargetGraph, FVector2D(0.0f, 0.0f));
        if (!ComponentToLocalNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create ComponentToLocalSpace node"));
        }
        bCreatedComponentToLocalNode = true;
    }
    RootNode->NodePosX = 240.0f;
    RootNode->NodePosY = 0.0f;

    bool bSettingsChanged = false;
    if (ModifyBoneNode->Node.BoneToModify.BoneName != TargetBoneName)
    {
        ModifyBoneNode->Node.BoneToModify.BoneName = TargetBoneName;
        bSettingsChanged = true;
    }
    if (!ModifyBoneNode->Node.Rotation.Equals(AdditiveRotation, KINDA_SMALL_NUMBER))
    {
        ModifyBoneNode->Node.Rotation = AdditiveRotation;
        bSettingsChanged = true;
    }
    if (UEdGraphPin* RotationPin = FUnrealMCPCommonUtils::FindPin(ModifyBoneNode, TEXT("Rotation"), EGPD_Input))
    {
        const FString RotationDefault = FString::Printf(
            TEXT("%f,%f,%f"),
            AdditiveRotation.Pitch,
            AdditiveRotation.Yaw,
            AdditiveRotation.Roll);
        if (!RotationPin->DefaultValue.Equals(RotationDefault, ESearchCase::CaseSensitive))
        {
            if (TargetGraph->GetSchema())
            {
                TargetGraph->GetSchema()->TrySetDefaultValue(*RotationPin, RotationDefault);
            }
            ModifyBoneNode->PinDefaultValueChanged(RotationPin);
            bSettingsChanged = true;
        }
    }
    if (ModifyBoneNode->Node.TranslationMode != BMM_Ignore)
    {
        ModifyBoneNode->Node.TranslationMode = BMM_Ignore;
        bSettingsChanged = true;
    }
    if (ModifyBoneNode->Node.RotationMode != BMM_Additive)
    {
        ModifyBoneNode->Node.RotationMode = BMM_Additive;
        bSettingsChanged = true;
    }
    if (ModifyBoneNode->Node.ScaleMode != BMM_Ignore)
    {
        ModifyBoneNode->Node.ScaleMode = BMM_Ignore;
        bSettingsChanged = true;
    }
    if (ModifyBoneNode->Node.TranslationSpace != BCS_BoneSpace)
    {
        ModifyBoneNode->Node.TranslationSpace = BCS_BoneSpace;
        bSettingsChanged = true;
    }
    if (ModifyBoneNode->Node.RotationSpace != BCS_BoneSpace)
    {
        ModifyBoneNode->Node.RotationSpace = BCS_BoneSpace;
        bSettingsChanged = true;
    }
    if (ModifyBoneNode->Node.ScaleSpace != BCS_BoneSpace)
    {
        ModifyBoneNode->Node.ScaleSpace = BCS_BoneSpace;
        bSettingsChanged = true;
    }

    UEdGraphPin* InputPoseOutput = FindFirstPosePin(InputPoseNode, EGPD_Output);
    UEdGraphPin* LocalToComponentInput = FindFirstPosePin(LocalToComponentNode, EGPD_Input, { TEXT("Pose") });
    UEdGraphPin* LocalToComponentOutput = FindFirstComponentPosePin(LocalToComponentNode, EGPD_Output);
    UEdGraphPin* ModifyBoneInput = FindFirstComponentPosePin(ModifyBoneNode, EGPD_Input, { TEXT("ComponentPose") });
    UEdGraphPin* ModifyBoneOutput = FindFirstComponentPosePin(ModifyBoneNode, EGPD_Output);
    UEdGraphPin* ComponentToLocalInput = FindFirstComponentPosePin(ComponentToLocalNode, EGPD_Input, { TEXT("ComponentPose") });
    UEdGraphPin* ComponentToLocalOutput = FindFirstPosePin(ComponentToLocalNode, EGPD_Output);
    UEdGraphPin* RootInput = FindFirstPosePin(RootNode, EGPD_Input, { TEXT("Result") });

    if (!InputPoseOutput || !LocalToComponentInput || !LocalToComponentOutput || !ModifyBoneInput || !ModifyBoneOutput || !ComponentToLocalInput || !ComponentToLocalOutput || !RootInput)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve one or more required pose pins for ModifyBone demo chain"));
    }

    bool bLinkChanged = false;
    bool bChangedThisLink = false;
    FString LinkError;
    TSharedPtr<FJsonObject> LinkErrorObj;
    if (!EnsureAnimGraphConnection(TargetGraph, InputPoseOutput, LocalToComponentInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, LocalToComponentOutput, ModifyBoneInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, ModifyBoneOutput, ComponentToLocalInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, ComponentToLocalOutput, RootInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    const bool bGraphChanged = bCreatedInputNode || bCreatedLocalToComponentNode || bCreatedModifyBoneNode || bCreatedComponentToLocalNode || bSettingsChanged || bLinkChanged;
    if (bGraphChanged)
    {
        FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        TargetGraph->NotifyGraphChanged();
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("connected"), true);
    ResultObj->SetBoolField(TEXT("graph_changed"), bGraphChanged);
    ResultObj->SetBoolField(TEXT("created_input_node"), bCreatedInputNode);
    ResultObj->SetBoolField(TEXT("created_local_to_component_node"), bCreatedLocalToComponentNode);
    ResultObj->SetBoolField(TEXT("created_modify_bone_node"), bCreatedModifyBoneNode);
    ResultObj->SetBoolField(TEXT("created_component_to_local_node"), bCreatedComponentToLocalNode);
    ResultObj->SetBoolField(TEXT("settings_changed"), bSettingsChanged);
    ResultObj->SetBoolField(TEXT("links_changed"), bLinkChanged);
    ResultObj->SetStringField(TEXT("bone_name"), BoneName);
    ResultObj->SetStringField(TEXT("rotation_mode"), TEXT("BMM_Additive"));
    ResultObj->SetStringField(TEXT("rotation_space"), TEXT("BCS_BoneSpace"));
    ResultObj->SetStringField(TEXT("rotation"), AdditiveRotation.ToString());
    ResultObj->SetObjectField(TEXT("input_pose_node"), NodeToJson(InputPoseNode, true));
    ResultObj->SetObjectField(TEXT("local_to_component_node"), NodeToJson(LocalToComponentNode, true));
    ResultObj->SetObjectField(TEXT("modify_bone_node"), NodeToJson(ModifyBoneNode, true));
    ResultObj->SetObjectField(TEXT("component_to_local_node"), NodeToJson(ComponentToLocalNode, true));
    ResultObj->SetObjectField(TEXT("root_node"), NodeToJson(RootNode, true));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleEnsureAnimGraphModifyCurveDemo(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString CurveError;
    const TArray<TPair<FName, float>> CurveEntries = ParseModifyCurveEntries(Params, CurveError);
    if (!CurveError.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(CurveError);
    }
    if (CurveEntries.Num() == 0)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("At least one curve entry is required"));
    }

    float Alpha = 1.0f;
    if (Params->HasField(TEXT("alpha")))
    {
        Alpha = FMath::Clamp(static_cast<float>(Params->GetNumberField(TEXT("alpha"))), 0.0f, 1.0f);
    }

    FString ApplyModeText;
    if (!Params->TryGetStringField(TEXT("apply_mode"), ApplyModeText))
    {
        ApplyModeText = TEXT("Add");
    }
    EModifyCurveApplyMode ApplyMode = EModifyCurveApplyMode::Add;
    if (!ParseModifyCurveApplyMode(ApplyModeText, ApplyMode))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Invalid 'apply_mode': '%s'. Use Add, Scale, Blend, WeightedMovingAverage, or RemapCurve."),
            *ApplyModeText));
    }

    bool bReplaceExisting = false;
    Params->TryGetBoolField(TEXT("replace_existing"), bReplaceExisting);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    bool bAllowNonSample = false;
    Params->TryGetBoolField(TEXT("allow_non_sample"), bAllowNonSample);
    if (!bAllowNonSample && !Blueprint->GetPathName().StartsWith(TEXT("/Game/_MCP_Sample/")))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Refusing to modify non-sample Anim Blueprint '%s'. Pass allow_non_sample=true only for intentional non-sample edits."),
            *Blueprint->GetPathName()));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    UAnimGraphNode_Root* RootNode = FindFirstNodeOfType<UAnimGraphNode_Root>(TargetGraph);
    if (!RootNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("AnimGraph root node not found in graph: %s"), *TargetGraph->GetName()));
    }

    bool bCreatedInputNode = false;
    UAnimGraphNode_LinkedInputPose* InputPoseNode = FindFirstNodeOfType<UAnimGraphNode_LinkedInputPose>(TargetGraph);
    if (!InputPoseNode)
    {
        InputPoseNode = AddAnimGraphNodeToGraph<UAnimGraphNode_LinkedInputPose>(TargetGraph, FVector2D(-480.0f, 0.0f));
        if (!InputPoseNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create LinkedInputPose node"));
        }
        bCreatedInputNode = true;
    }

    bool bCreatedModifyCurveNode = false;
    UAnimGraphNode_ModifyCurve* ModifyCurveNode = FindFirstNodeOfType<UAnimGraphNode_ModifyCurve>(TargetGraph);
    if (!ModifyCurveNode)
    {
        ModifyCurveNode = AddAnimGraphNodeToGraph<UAnimGraphNode_ModifyCurve>(TargetGraph, FVector2D(-240.0f, 0.0f));
        if (!ModifyCurveNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create ModifyCurve node"));
        }
        bCreatedModifyCurveNode = true;
    }

    RootNode->NodePosX = 0.0f;
    RootNode->NodePosY = 0.0f;

    FAnimNode_ModifyCurve* ModifyCurveAnimNode = GetMutableModifyCurveAnimNode(ModifyCurveNode);
    if (!ModifyCurveAnimNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve internal FAnimNode_ModifyCurve settings"));
    }

    bool bSettingsChanged = false;
    bool bCurvePinsChanged = false;
    TArray<FString> ChangedFields;

    if (!ModifyCurveEntriesMatchNode(ModifyCurveAnimNode, CurveEntries))
    {
        ModifyCurveNode->Modify();
        ModifyCurveAnimNode->CurveNames.Reset();
        ModifyCurveAnimNode->CurveValues.Reset();
        ModifyCurveAnimNode->CurveMap.Reset();
        for (const TPair<FName, float>& Entry : CurveEntries)
        {
            ModifyCurveAnimNode->CurveNames.Add(Entry.Key);
            ModifyCurveAnimNode->CurveValues.Add(Entry.Value);
            ModifyCurveAnimNode->CurveMap.Add(Entry.Key, Entry.Value);
        }
        ModifyCurveNode->ReconstructNode();
        bSettingsChanged = true;
        bCurvePinsChanged = true;
        ChangedFields.Add(TEXT("Curves"));
    }

    if (!FMath::IsNearlyEqual(ModifyCurveAnimNode->Alpha, Alpha, KINDA_SMALL_NUMBER))
    {
        ModifyCurveAnimNode->Alpha = Alpha;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("Alpha"));
    }
    if (UEdGraphPin* AlphaPin = FUnrealMCPCommonUtils::FindPin(ModifyCurveNode, TEXT("Alpha"), EGPD_Input))
    {
        const FString AlphaDefault = FString::SanitizeFloat(Alpha);
        if (!AlphaPin->DefaultValue.Equals(AlphaDefault, ESearchCase::CaseSensitive))
        {
            if (TargetGraph->GetSchema())
            {
                TargetGraph->GetSchema()->TrySetDefaultValue(*AlphaPin, AlphaDefault);
            }
            ModifyCurveNode->PinDefaultValueChanged(AlphaPin);
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("AlphaPin"));
        }
    }

    if (ModifyCurveAnimNode->ApplyMode != ApplyMode)
    {
        ModifyCurveAnimNode->ApplyMode = ApplyMode;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("ApplyMode"));
    }

    for (const TPair<FName, float>& Entry : CurveEntries)
    {
        const FString CurveName = Entry.Key.ToString();
        UEdGraphPin* CurvePin = nullptr;
        for (UEdGraphPin* Pin : ModifyCurveNode->Pins)
        {
            if (Pin && Pin->Direction == EGPD_Input && Pin->PinFriendlyName.ToString().Equals(CurveName, ESearchCase::CaseSensitive))
            {
                CurvePin = Pin;
                break;
            }
        }

        if (CurvePin)
        {
            const FString CurveDefault = FString::SanitizeFloat(Entry.Value);
            if (!CurvePin->DefaultValue.Equals(CurveDefault, ESearchCase::CaseSensitive))
            {
                if (TargetGraph->GetSchema())
                {
                    TargetGraph->GetSchema()->TrySetDefaultValue(*CurvePin, CurveDefault);
                }
                ModifyCurveNode->PinDefaultValueChanged(CurvePin);
                bSettingsChanged = true;
                ChangedFields.Add(FString::Printf(TEXT("CurvePin:%s"), *CurveName));
            }
        }
    }

    UEdGraphPin* InputPoseOutput = FindFirstPosePin(InputPoseNode, EGPD_Output);
    UEdGraphPin* ModifyCurveInput = FindFirstPosePin(ModifyCurveNode, EGPD_Input, { TEXT("SourcePose") });
    UEdGraphPin* ModifyCurveOutput = FindFirstPosePin(ModifyCurveNode, EGPD_Output);
    UEdGraphPin* RootInput = FindFirstPosePin(RootNode, EGPD_Input, { TEXT("Result") });

    if (!InputPoseOutput || !ModifyCurveInput || !ModifyCurveOutput || !RootInput)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve one or more required pose pins for ModifyCurve demo chain"));
    }

    bool bLinkChanged = false;
    bool bChangedThisLink = false;
    FString LinkError;
    TSharedPtr<FJsonObject> LinkErrorObj;
    if (!EnsureAnimGraphConnection(TargetGraph, InputPoseOutput, ModifyCurveInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, ModifyCurveOutput, RootInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    const bool bGraphChanged = bCreatedInputNode || bCreatedModifyCurveNode || bSettingsChanged || bLinkChanged;
    if (bGraphChanged)
    {
        if (bCurvePinsChanged)
        {
            FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
        }
        else
        {
            FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        }
        TargetGraph->NotifyGraphChanged();
    }

    TArray<TSharedPtr<FJsonValue>> ChangedFieldValues;
    for (const FString& FieldName : ChangedFields)
    {
        ChangedFieldValues.Add(MakeShared<FJsonValueString>(FieldName));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("connected"), true);
    ResultObj->SetBoolField(TEXT("graph_changed"), bGraphChanged);
    ResultObj->SetBoolField(TEXT("created_input_node"), bCreatedInputNode);
    ResultObj->SetBoolField(TEXT("created_modify_curve_node"), bCreatedModifyCurveNode);
    ResultObj->SetBoolField(TEXT("settings_changed"), bSettingsChanged);
    ResultObj->SetBoolField(TEXT("links_changed"), bLinkChanged);
    ResultObj->SetNumberField(TEXT("alpha"), Alpha);
    ResultObj->SetStringField(TEXT("apply_mode"), GetModifyCurveApplyModeName(ApplyMode));
    ResultObj->SetObjectField(TEXT("curve_values"), ModifyCurveEntriesToJsonObject(CurveEntries));
    ResultObj->SetArrayField(TEXT("changed_fields"), ChangedFieldValues);
    ResultObj->SetObjectField(TEXT("input_pose_node"), NodeToJson(InputPoseNode, true));
    ResultObj->SetObjectField(TEXT("modify_curve_node"), NodeToJson(ModifyCurveNode, true));
    ResultObj->SetObjectField(TEXT("root_node"), NodeToJson(RootNode, true));
    ResultObj->SetObjectField(TEXT("settings"), AnimGraphNodeSettingsToJson(ModifyCurveNode, 4));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSetAnimGraphControlRigInputDefaults(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString DefaultsError;
    const TArray<FControlRigInputDefaultRequest> DefaultRequests = ParseControlRigInputDefaults(Params, DefaultsError);
    if (!DefaultsError.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(DefaultsError);
    }
    if (DefaultRequests.Num() == 0)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("At least one ControlRig input default is required"));
    }

    bool bDisconnectExistingLinks = false;
    Params->TryGetBoolField(TEXT("disconnect_existing_links"), bDisconnectExistingLinks);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    bool bAllowNonSample = false;
    Params->TryGetBoolField(TEXT("allow_non_sample"), bAllowNonSample);
    if (!bAllowNonSample && !Blueprint->GetPathName().StartsWith(TEXT("/Game/_MCP_Sample/")))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Refusing to modify non-sample Anim Blueprint '%s'. Pass allow_non_sample=true only for intentional non-sample edits."),
            *Blueprint->GetPathName()));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    const UEdGraphSchema_K2* K2Schema = Cast<UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph schema is not K2-compatible: %s"),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    int32 ControlRigCandidateCount = 0;
    FString ResolveError;
    UAnimGraphNode_ControlRig* ControlRigNode = ResolveControlRigNodeForInputDefaults(TargetGraph, Params, ControlRigCandidateCount, ResolveError);
    if (!ControlRigNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(ResolveError);
    }

    ControlRigNode->Modify();
    ControlRigNode->ReconstructNode();

    TArray<FName> AvailableInputNames = GetControlRigCustomPinNamesByReflection(ControlRigNode);
    bool bVisibilityChanged = false;
    TArray<TSharedPtr<FJsonValue>> PerInputResults;
    TArray<FString> ChangedFields;

    for (const FControlRigInputDefaultRequest& Request : DefaultRequests)
    {
        bool bFound = false;
        bool bChangedThisPinVisibility = false;
        FString VisibilityError;
        if (!SetControlRigCustomPinVisibleByReflection(ControlRigNode, Request.PropertyName, true, bFound, bChangedThisPinVisibility, VisibilityError))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(VisibilityError);
        }

        if (!bFound)
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("ControlRig input '%s' is not available on node '%s'"),
                *Request.PropertyName.ToString(),
                *ControlRigNode->GetName()));
            ErrorObj->SetArrayField(TEXT("available_input_names"), NamesToJsonArray(AvailableInputNames));
            ErrorObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        if (bChangedThisPinVisibility)
        {
            bVisibilityChanged = true;
            ChangedFields.Add(FString::Printf(TEXT("ExposePin:%s"), *Request.PropertyName.ToString()));
        }
    }

    if (bVisibilityChanged)
    {
        ControlRigNode->ReconstructNode();
        AvailableInputNames = GetControlRigCustomPinNamesByReflection(ControlRigNode);
    }

    bool bDefaultChanged = false;
    bool bLinksChanged = false;
    for (const FControlRigInputDefaultRequest& Request : DefaultRequests)
    {
        UEdGraphPin* InputPin = FindControlRigInputPin(ControlRigNode, Request.PropertyName);
        if (!InputPin)
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("ControlRig input pin '%s' was not found after exposing it"),
                *Request.PropertyName.ToString()));
            ErrorObj->SetArrayField(TEXT("available_input_names"), NamesToJsonArray(AvailableInputNames));
            ErrorObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        const int32 LinkedPinCountBefore = InputPin->LinkedTo.Num();
        if (bDisconnectExistingLinks && LinkedPinCountBefore > 0)
        {
            K2Schema->BreakPinLinks(*InputPin, true);
            ControlRigNode->PinConnectionListChanged(InputPin);
            bLinksChanged = true;
            ChangedFields.Add(FString::Printf(TEXT("BreakLinks:%s"), *Request.PropertyName.ToString()));
        }

        const FString PreviousDefaultValue = InputPin->GetDefaultAsString();
        FString AppliedValue;
        FString DefaultError;
        FString RequestedDefaultValue;
        const bool bDefaultAlreadyMatches = PinDefaultSemanticallyMatchesJsonValue(InputPin, Request.Value, K2Schema, RequestedDefaultValue);
        if (bDefaultAlreadyMatches)
        {
            AppliedValue = RequestedDefaultValue.IsEmpty() ? PreviousDefaultValue : RequestedDefaultValue;
        }
        else if (!ApplyPinDefaultValueChecked(InputPin, Request.Value, K2Schema, AppliedValue, DefaultError))
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("Failed to set ControlRig input '%s' default: %s"),
                *Request.PropertyName.ToString(),
                *DefaultError));
            ErrorObj->SetStringField(TEXT("pin_name"), Request.PropertyName.ToString());
            ErrorObj->SetStringField(TEXT("previous_default_value"), PreviousDefaultValue);
            ErrorObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        if (!bDefaultAlreadyMatches)
        {
            ControlRigNode->PinDefaultValueChanged(InputPin);
        }
        const FString CurrentDefaultValue = InputPin->GetDefaultAsString();
        const bool bChangedThisDefault = !bDefaultAlreadyMatches && !PreviousDefaultValue.Equals(CurrentDefaultValue, ESearchCase::CaseSensitive);
        if (bChangedThisDefault)
        {
            bDefaultChanged = true;
            ChangedFields.Add(FString::Printf(TEXT("Default:%s"), *Request.PropertyName.ToString()));
        }

        TSharedPtr<FJsonObject> InputResult = MakeShared<FJsonObject>();
        InputResult->SetStringField(TEXT("name"), Request.PropertyName.ToString());
        InputResult->SetField(TEXT("requested_value"), Request.Value);
        InputResult->SetBoolField(TEXT("pin_found"), true);
        InputResult->SetBoolField(TEXT("default_changed"), bChangedThisDefault);
        InputResult->SetBoolField(TEXT("default_already_matched"), bDefaultAlreadyMatches);
        InputResult->SetBoolField(TEXT("pin_linked"), InputPin->LinkedTo.Num() > 0);
        InputResult->SetNumberField(TEXT("linked_pin_count_before"), LinkedPinCountBefore);
        InputResult->SetNumberField(TEXT("linked_pin_count"), InputPin->LinkedTo.Num());
        InputResult->SetBoolField(TEXT("links_disconnected"), bDisconnectExistingLinks && LinkedPinCountBefore > 0);
        InputResult->SetStringField(TEXT("previous_default_value"), PreviousDefaultValue);
        InputResult->SetStringField(TEXT("applied_default_value"), AppliedValue);
        InputResult->SetStringField(TEXT("current_default_value"), CurrentDefaultValue);
        InputResult->SetStringField(TEXT("pin_type_category"), InputPin->PinType.PinCategory.ToString());
        if (InputPin->PinType.PinSubCategoryObject.IsValid())
        {
            InputResult->SetStringField(TEXT("pin_subcategory_object"), InputPin->PinType.PinSubCategoryObject->GetPathName());
        }
        PerInputResults.Add(MakeShared<FJsonValueObject>(InputResult));
    }

    const bool bGraphChanged = bVisibilityChanged || bDefaultChanged || bLinksChanged;
    if (bGraphChanged)
    {
        if (bVisibilityChanged)
        {
            FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
        }
        else
        {
            FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        }
        TargetGraph->NotifyGraphChanged();
    }

    TArray<TSharedPtr<FJsonValue>> ChangedFieldValues;
    for (const FString& FieldName : ChangedFields)
    {
        ChangedFieldValues.Add(MakeShared<FJsonValueString>(FieldName));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("connected"), true);
    ResultObj->SetBoolField(TEXT("graph_changed"), bGraphChanged);
    ResultObj->SetBoolField(TEXT("visibility_changed"), bVisibilityChanged);
    ResultObj->SetBoolField(TEXT("defaults_changed"), bDefaultChanged);
    ResultObj->SetBoolField(TEXT("links_changed"), bLinksChanged);
    ResultObj->SetBoolField(TEXT("disconnect_existing_links"), bDisconnectExistingLinks);
    ResultObj->SetNumberField(TEXT("controlrig_candidate_count"), ControlRigCandidateCount);
    ResultObj->SetStringField(TEXT("control_rig_class"), GetControlRigClassPathFromNode(ControlRigNode));
    ResultObj->SetObjectField(TEXT("requested_input_defaults"), ControlRigInputDefaultsToJsonObject(DefaultRequests));
    ResultObj->SetArrayField(TEXT("input_results"), PerInputResults);
    ResultObj->SetArrayField(TEXT("available_input_names"), NamesToJsonArray(AvailableInputNames));
    ResultObj->SetArrayField(TEXT("changed_fields"), ChangedFieldValues);
    ResultObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
    ResultObj->SetObjectField(TEXT("settings"), AnimGraphNodeSettingsToJson(ControlRigNode, 4));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleEnsureControlRigForcedDriverAnimBP(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString CurveError;
    const TArray<TPair<FName, float>> CurveEntries = ParseModifyCurveEntries(Params, CurveError);
    if (!CurveError.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(CurveError);
    }
    if (CurveEntries.Num() == 0)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("At least one curve entry is required"));
    }

    FString DefaultsError;
    const TArray<FControlRigInputDefaultRequest> DefaultRequests = ParseControlRigInputDefaults(Params, DefaultsError);
    if (!DefaultsError.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(DefaultsError);
    }
    if (DefaultRequests.Num() == 0)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("At least one ControlRig input default is required"));
    }

    float Alpha = 1.0f;
    if (Params->HasField(TEXT("alpha")))
    {
        Alpha = FMath::Clamp(static_cast<float>(Params->GetNumberField(TEXT("alpha"))), 0.0f, 1.0f);
    }

    FString ApplyModeText;
    if (!Params->TryGetStringField(TEXT("apply_mode"), ApplyModeText))
    {
        ApplyModeText = TEXT("Add");
    }
    EModifyCurveApplyMode ApplyMode = EModifyCurveApplyMode::Add;
    if (!ParseModifyCurveApplyMode(ApplyModeText, ApplyMode))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Invalid 'apply_mode': '%s'. Use Add, Scale, Blend, WeightedMovingAverage, or RemapCurve."),
            *ApplyModeText));
    }

    bool bReplaceExisting = true;
    Params->TryGetBoolField(TEXT("replace_existing"), bReplaceExisting);

    bool bDisconnectExistingLinks = true;
    Params->TryGetBoolField(TEXT("disconnect_existing_links"), bDisconnectExistingLinks);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    bool bAllowNonSample = false;
    Params->TryGetBoolField(TEXT("allow_non_sample"), bAllowNonSample);
    if (!bAllowNonSample && !Blueprint->GetPathName().StartsWith(TEXT("/Game/_MCP_Sample/")))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Refusing to modify non-sample Anim Blueprint '%s'. Pass allow_non_sample=true only for intentional non-sample edits."),
            *Blueprint->GetPathName()));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    const UEdGraphSchema_K2* K2Schema = Cast<UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph schema is not K2-compatible: %s"),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    int32 ControlRigCandidateCount = 0;
    FString ResolveError;
    UAnimGraphNode_ControlRig* ControlRigNode = ResolveControlRigNodeForInputDefaults(TargetGraph, Params, ControlRigCandidateCount, ResolveError);
    if (!ControlRigNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(ResolveError);
    }

    ControlRigNode->Modify();
    ControlRigNode->ReconstructNode();

    UEdGraphPin* ControlRigSourceInput = FindFirstPosePin(ControlRigNode, EGPD_Input, { TEXT("Source") });
    if (!ControlRigSourceInput)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("ControlRig Source pose input pin not found"));
    }

    bool bCreatedModifyCurveNode = false;
    bool bCurveInsertedBeforeControlRig = false;
    UAnimGraphNode_ModifyCurve* ModifyCurveNode = FindModifyCurveFeedingControlRig(ControlRigNode);
    if (!ModifyCurveNode)
    {
        ModifyCurveNode = AddAnimGraphNodeToGraph<UAnimGraphNode_ModifyCurve>(
            TargetGraph,
            FVector2D(ControlRigNode->NodePosX - 260.0f, ControlRigNode->NodePosY));
        if (!ModifyCurveNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create ModifyCurve node for ControlRig forced driver"));
        }
        bCreatedModifyCurveNode = true;
    }
    else
    {
        bCurveInsertedBeforeControlRig = true;
    }

    FAnimNode_ModifyCurve* ModifyCurveAnimNode = GetMutableModifyCurveAnimNode(ModifyCurveNode);
    if (!ModifyCurveAnimNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve internal FAnimNode_ModifyCurve settings"));
    }

    bool bSettingsChanged = false;
    bool bCurvePinsChanged = false;
    TArray<FString> ChangedFields;

    if (!ModifyCurveEntriesMatchNode(ModifyCurveAnimNode, CurveEntries))
    {
        ModifyCurveNode->Modify();
        ModifyCurveAnimNode->CurveNames.Reset();
        ModifyCurveAnimNode->CurveValues.Reset();
        ModifyCurveAnimNode->CurveMap.Reset();
        for (const TPair<FName, float>& Entry : CurveEntries)
        {
            ModifyCurveAnimNode->CurveNames.Add(Entry.Key);
            ModifyCurveAnimNode->CurveValues.Add(Entry.Value);
            ModifyCurveAnimNode->CurveMap.Add(Entry.Key, Entry.Value);
        }
        ModifyCurveNode->ReconstructNode();
        bSettingsChanged = true;
        bCurvePinsChanged = true;
        ChangedFields.Add(TEXT("Curves"));
    }

    if (!FMath::IsNearlyEqual(ModifyCurveAnimNode->Alpha, Alpha, KINDA_SMALL_NUMBER))
    {
        ModifyCurveAnimNode->Alpha = Alpha;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("Alpha"));
    }
    if (UEdGraphPin* AlphaPin = FUnrealMCPCommonUtils::FindPin(ModifyCurveNode, TEXT("Alpha"), EGPD_Input))
    {
        const FString AlphaDefault = FString::SanitizeFloat(Alpha);
        if (!AlphaPin->DefaultValue.Equals(AlphaDefault, ESearchCase::CaseSensitive))
        {
            TargetGraph->GetSchema()->TrySetDefaultValue(*AlphaPin, AlphaDefault);
            ModifyCurveNode->PinDefaultValueChanged(AlphaPin);
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("AlphaPin"));
        }
    }

    if (ModifyCurveAnimNode->ApplyMode != ApplyMode)
    {
        ModifyCurveAnimNode->ApplyMode = ApplyMode;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("ApplyMode"));
    }

    for (const TPair<FName, float>& Entry : CurveEntries)
    {
        const FString CurveName = Entry.Key.ToString();
        UEdGraphPin* CurvePin = nullptr;
        for (UEdGraphPin* Pin : ModifyCurveNode->Pins)
        {
            if (Pin && Pin->Direction == EGPD_Input && Pin->PinFriendlyName.ToString().Equals(CurveName, ESearchCase::CaseSensitive))
            {
                CurvePin = Pin;
                break;
            }
        }

        if (CurvePin)
        {
            const FString CurveDefault = FString::SanitizeFloat(Entry.Value);
            if (!CurvePin->DefaultValue.Equals(CurveDefault, ESearchCase::CaseSensitive))
            {
                TargetGraph->GetSchema()->TrySetDefaultValue(*CurvePin, CurveDefault);
                ModifyCurveNode->PinDefaultValueChanged(CurvePin);
                bSettingsChanged = true;
                ChangedFields.Add(FString::Printf(TEXT("CurvePin:%s"), *CurveName));
            }
        }
    }

    UEdGraphPin* ModifyCurveInput = FindFirstPosePin(ModifyCurveNode, EGPD_Input, { TEXT("SourcePose") });
    UEdGraphPin* ModifyCurveOutput = FindFirstPosePin(ModifyCurveNode, EGPD_Output);
    ControlRigSourceInput = FindFirstPosePin(ControlRigNode, EGPD_Input, { TEXT("Source") });
    if (!ModifyCurveInput || !ModifyCurveOutput || !ControlRigSourceInput)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve required ControlRig forced-driver pose pins"));
    }

    UEdGraphPin* UpstreamPoseOutput = nullptr;
    if (ControlRigSourceInput->LinkedTo.Contains(ModifyCurveOutput))
    {
        bCurveInsertedBeforeControlRig = true;
        UpstreamPoseOutput = ModifyCurveInput->LinkedTo.Num() > 0 ? ModifyCurveInput->LinkedTo[0] : nullptr;
    }
    else
    {
        UpstreamPoseOutput = ControlRigSourceInput->LinkedTo.Num() > 0 ? ControlRigSourceInput->LinkedTo[0] : nullptr;
    }

    if (!UpstreamPoseOutput)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("ControlRig Source pose input has no upstream pose to route through ModifyCurve"));
    }

    bool bPoseLinksChanged = false;
    bool bChangedThisLink = false;
    FString LinkError;
    TSharedPtr<FJsonObject> LinkErrorObj;
    if (!EnsureAnimGraphConnection(TargetGraph, UpstreamPoseOutput, ModifyCurveInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bPoseLinksChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, ModifyCurveOutput, ControlRigSourceInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bPoseLinksChanged |= bChangedThisLink;
    bCurveInsertedBeforeControlRig = true;

    TArray<FName> AvailableInputNames = GetControlRigCustomPinNamesByReflection(ControlRigNode);
    bool bVisibilityChanged = false;
    bool bDefaultChanged = false;
    bool bInputLinksChanged = false;
    TArray<TSharedPtr<FJsonValue>> PerInputResults;

    for (const FControlRigInputDefaultRequest& Request : DefaultRequests)
    {
        bool bFound = false;
        bool bChangedThisPinVisibility = false;
        FString VisibilityError;
        if (!SetControlRigCustomPinVisibleByReflection(ControlRigNode, Request.PropertyName, true, bFound, bChangedThisPinVisibility, VisibilityError))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(VisibilityError);
        }

        if (!bFound)
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("ControlRig input '%s' is not available on node '%s'"),
                *Request.PropertyName.ToString(),
                *ControlRigNode->GetName()));
            ErrorObj->SetArrayField(TEXT("available_input_names"), NamesToJsonArray(AvailableInputNames));
            ErrorObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        if (bChangedThisPinVisibility)
        {
            bVisibilityChanged = true;
            ChangedFields.Add(FString::Printf(TEXT("ExposePin:%s"), *Request.PropertyName.ToString()));
        }
    }

    if (bVisibilityChanged)
    {
        ControlRigNode->ReconstructNode();
        AvailableInputNames = GetControlRigCustomPinNamesByReflection(ControlRigNode);
    }

    for (const FControlRigInputDefaultRequest& Request : DefaultRequests)
    {
        UEdGraphPin* InputPin = FindControlRigInputPin(ControlRigNode, Request.PropertyName);
        if (!InputPin)
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("ControlRig input pin '%s' was not found after exposing it"),
                *Request.PropertyName.ToString()));
            ErrorObj->SetArrayField(TEXT("available_input_names"), NamesToJsonArray(AvailableInputNames));
            ErrorObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        const int32 LinkedPinCountBefore = InputPin->LinkedTo.Num();
        if (bDisconnectExistingLinks && LinkedPinCountBefore > 0)
        {
            K2Schema->BreakPinLinks(*InputPin, true);
            ControlRigNode->PinConnectionListChanged(InputPin);
            bInputLinksChanged = true;
            ChangedFields.Add(FString::Printf(TEXT("BreakLinks:%s"), *Request.PropertyName.ToString()));
        }

        const FString PreviousDefaultValue = InputPin->GetDefaultAsString();
        FString AppliedValue;
        FString DefaultError;
        FString RequestedDefaultValue;
        const bool bDefaultAlreadyMatches = PinDefaultSemanticallyMatchesJsonValue(InputPin, Request.Value, K2Schema, RequestedDefaultValue);
        if (bDefaultAlreadyMatches)
        {
            AppliedValue = RequestedDefaultValue.IsEmpty() ? PreviousDefaultValue : RequestedDefaultValue;
        }
        else if (!ApplyPinDefaultValueChecked(InputPin, Request.Value, K2Schema, AppliedValue, DefaultError))
        {
            TSharedPtr<FJsonObject> ErrorObj = FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
                TEXT("Failed to set ControlRig input '%s' default: %s"),
                *Request.PropertyName.ToString(),
                *DefaultError));
            ErrorObj->SetStringField(TEXT("pin_name"), Request.PropertyName.ToString());
            ErrorObj->SetStringField(TEXT("previous_default_value"), PreviousDefaultValue);
            ErrorObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
            AddGraphField(ErrorObj, Blueprint, TargetGraph);
            return ErrorObj;
        }

        if (!bDefaultAlreadyMatches)
        {
            ControlRigNode->PinDefaultValueChanged(InputPin);
        }
        const FString CurrentDefaultValue = InputPin->GetDefaultAsString();
        const bool bChangedThisDefault = !bDefaultAlreadyMatches && !PreviousDefaultValue.Equals(CurrentDefaultValue, ESearchCase::CaseSensitive);
        if (bChangedThisDefault)
        {
            bDefaultChanged = true;
            ChangedFields.Add(FString::Printf(TEXT("Default:%s"), *Request.PropertyName.ToString()));
        }

        TSharedPtr<FJsonObject> InputResult = MakeShared<FJsonObject>();
        InputResult->SetStringField(TEXT("name"), Request.PropertyName.ToString());
        InputResult->SetField(TEXT("requested_value"), Request.Value);
        InputResult->SetBoolField(TEXT("pin_found"), true);
        InputResult->SetBoolField(TEXT("default_changed"), bChangedThisDefault);
        InputResult->SetBoolField(TEXT("default_already_matched"), bDefaultAlreadyMatches);
        InputResult->SetBoolField(TEXT("pin_linked"), InputPin->LinkedTo.Num() > 0);
        InputResult->SetNumberField(TEXT("linked_pin_count_before"), LinkedPinCountBefore);
        InputResult->SetNumberField(TEXT("linked_pin_count"), InputPin->LinkedTo.Num());
        InputResult->SetBoolField(TEXT("links_disconnected"), bDisconnectExistingLinks && LinkedPinCountBefore > 0);
        InputResult->SetStringField(TEXT("previous_default_value"), PreviousDefaultValue);
        InputResult->SetStringField(TEXT("applied_default_value"), AppliedValue);
        InputResult->SetStringField(TEXT("current_default_value"), CurrentDefaultValue);
        InputResult->SetStringField(TEXT("pin_type_category"), InputPin->PinType.PinCategory.ToString());
        if (InputPin->PinType.PinSubCategoryObject.IsValid())
        {
            InputResult->SetStringField(TEXT("pin_subcategory_object"), InputPin->PinType.PinSubCategoryObject->GetPathName());
        }
        PerInputResults.Add(MakeShared<FJsonValueObject>(InputResult));
    }

    const bool bGraphChanged = bCreatedModifyCurveNode || bSettingsChanged || bPoseLinksChanged || bVisibilityChanged || bDefaultChanged || bInputLinksChanged;
    if (bGraphChanged)
    {
        if (bCurvePinsChanged || bVisibilityChanged)
        {
            FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
        }
        else
        {
            FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        }
        TargetGraph->NotifyGraphChanged();
    }

    TArray<TSharedPtr<FJsonValue>> ChangedFieldValues;
    for (const FString& FieldName : ChangedFields)
    {
        ChangedFieldValues.Add(MakeShared<FJsonValueString>(FieldName));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("connected"), true);
    ResultObj->SetBoolField(TEXT("graph_changed"), bGraphChanged);
    ResultObj->SetBoolField(TEXT("created_modify_curve_node"), bCreatedModifyCurveNode);
    ResultObj->SetBoolField(TEXT("curve_inserted_before_controlrig"), bCurveInsertedBeforeControlRig);
    ResultObj->SetBoolField(TEXT("curve_settings_changed"), bSettingsChanged);
    ResultObj->SetBoolField(TEXT("pose_links_changed"), bPoseLinksChanged);
    ResultObj->SetBoolField(TEXT("visibility_changed"), bVisibilityChanged);
    ResultObj->SetBoolField(TEXT("defaults_changed"), bDefaultChanged);
    ResultObj->SetBoolField(TEXT("input_links_changed"), bInputLinksChanged);
    ResultObj->SetBoolField(TEXT("disconnect_existing_links"), bDisconnectExistingLinks);
    ResultObj->SetBoolField(TEXT("replace_existing"), bReplaceExisting);
    ResultObj->SetNumberField(TEXT("alpha"), Alpha);
    ResultObj->SetStringField(TEXT("apply_mode"), GetModifyCurveApplyModeName(ApplyMode));
    ResultObj->SetStringField(TEXT("control_rig_class"), GetControlRigClassPathFromNode(ControlRigNode));
    ResultObj->SetObjectField(TEXT("curve_values"), ModifyCurveEntriesToJsonObject(CurveEntries));
    ResultObj->SetObjectField(TEXT("requested_input_defaults"), ControlRigInputDefaultsToJsonObject(DefaultRequests));
    ResultObj->SetArrayField(TEXT("input_results"), PerInputResults);
    ResultObj->SetArrayField(TEXT("available_input_names"), NamesToJsonArray(AvailableInputNames));
    ResultObj->SetArrayField(TEXT("changed_fields"), ChangedFieldValues);
    ResultObj->SetObjectField(TEXT("upstream_pose_pin"), PinToJson(UpstreamPoseOutput));
    ResultObj->SetObjectField(TEXT("modify_curve_node"), NodeToJson(ModifyCurveNode, true));
    ResultObj->SetObjectField(TEXT("control_rig_node"), NodeToJson(ControlRigNode, true));
    ResultObj->SetObjectField(TEXT("modify_curve_settings"), AnimGraphNodeSettingsToJson(ModifyCurveNode, 4));
    ResultObj->SetObjectField(TEXT("control_rig_settings"), AnimGraphNodeSettingsToJson(ControlRigNode, 4));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleEnsureAnimGraphTrailDemo(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString TrailBoneName;
    if (!Params->TryGetStringField(TEXT("trail_bone"), TrailBoneName))
    {
        TrailBoneName = TEXT("VB VBHead");
    }
    TrailBoneName.TrimStartAndEndInline();
    if (TrailBoneName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'trail_bone' cannot be empty"));
    }
    const FName TargetTrailBoneName(*TrailBoneName);

    FString BaseJointName;
    if (!Params->TryGetStringField(TEXT("base_joint"), BaseJointName))
    {
        BaseJointName = TEXT("head");
    }
    BaseJointName.TrimStartAndEndInline();
    if (BaseJointName.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("'base_joint' cannot be empty"));
    }
    const FName TargetBaseJointName(*BaseJointName);

    int32 ChainLength = 2;
    if (Params->HasField(TEXT("chain_length")))
    {
        ChainLength = FMath::Max(2, FMath::RoundToInt(Params->GetNumberField(TEXT("chain_length"))));
    }

    FString ChainAxisText;
    if (!Params->TryGetStringField(TEXT("chain_bone_axis"), ChainAxisText))
    {
        ChainAxisText = TEXT("X");
    }
    EAxis::Type ChainBoneAxis = EAxis::X;
    if (!ParseTrailChainBoneAxis(ChainAxisText, ChainBoneAxis))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Invalid 'chain_bone_axis': '%s'. Use X, Y, or Z."),
            *ChainAxisText));
    }

    float Alpha = 1.0f;
    if (Params->HasField(TEXT("alpha")))
    {
        Alpha = static_cast<float>(Params->GetNumberField(TEXT("alpha")));
    }

    float RelaxationSpeedScale = 1.0f;
    if (Params->HasField(TEXT("relaxation_speed_scale")))
    {
        RelaxationSpeedScale = static_cast<float>(Params->GetNumberField(TEXT("relaxation_speed_scale")));
    }

    FVector FakeVelocity = FVector::ZeroVector;
    if (Params->HasField(TEXT("fake_velocity")))
    {
        FakeVelocity = FUnrealMCPCommonUtils::GetVectorFromJson(Params, TEXT("fake_velocity"));
    }

    bool bInvertChainBoneAxis = false;
    Params->TryGetBoolField(TEXT("invert_chain_bone_axis"), bInvertChainBoneAxis);

    bool bReorientParentToChild = true;
    Params->TryGetBoolField(TEXT("reorient_parent_to_child"), bReorientParentToChild);

    bool bActorSpaceFakeVelocity = false;
    Params->TryGetBoolField(TEXT("actor_space_fake_velocity"), bActorSpaceFakeVelocity);

    bool bLimitStretch = false;
    Params->TryGetBoolField(TEXT("limit_stretch"), bLimitStretch);

    float StretchLimit = 0.0f;
    if (Params->HasField(TEXT("stretch_limit")))
    {
        StretchLimit = static_cast<float>(Params->GetNumberField(TEXT("stretch_limit")));
    }

    float MaxDeltaTime = 0.0f;
    if (Params->HasField(TEXT("max_delta_time")))
    {
        MaxDeltaTime = static_cast<float>(Params->GetNumberField(TEXT("max_delta_time")));
    }

    bool bReplaceExisting = false;
    Params->TryGetBoolField(TEXT("replace_existing"), bReplaceExisting);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    bool bAllowNonSample = false;
    Params->TryGetBoolField(TEXT("allow_non_sample"), bAllowNonSample);
    if (!bAllowNonSample && !Blueprint->GetPathName().StartsWith(TEXT("/Game/_MCP_Sample/")))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Refusing to modify non-sample Anim Blueprint '%s'. Pass allow_non_sample=true only for intentional non-sample edits."),
            *Blueprint->GetPathName()));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    if (!IsAnimationGraph(TargetGraph))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Target graph is not an AnimationGraph. graph='%s' schema='%s'"),
            *TargetGraph->GetName(),
            TargetGraph->GetSchema() ? *TargetGraph->GetSchema()->GetClass()->GetName() : TEXT("<none>")));
    }

    UAnimGraphNode_Root* RootNode = FindFirstNodeOfType<UAnimGraphNode_Root>(TargetGraph);
    if (!RootNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("AnimGraph root node not found in graph: %s"), *TargetGraph->GetName()));
    }

    bool bCreatedInputNode = false;
    UAnimGraphNode_LinkedInputPose* InputPoseNode = FindFirstNodeOfType<UAnimGraphNode_LinkedInputPose>(TargetGraph);
    if (!InputPoseNode)
    {
        InputPoseNode = AddAnimGraphNodeToGraph<UAnimGraphNode_LinkedInputPose>(TargetGraph, FVector2D(-960.0f, 0.0f));
        if (!InputPoseNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create LinkedInputPose node"));
        }
        bCreatedInputNode = true;
    }

    bool bCreatedLocalToComponentNode = false;
    UAnimGraphNode_LocalToComponentSpace* LocalToComponentNode = FindFirstNodeOfType<UAnimGraphNode_LocalToComponentSpace>(TargetGraph);
    if (!LocalToComponentNode)
    {
        LocalToComponentNode = AddAnimGraphNodeToGraph<UAnimGraphNode_LocalToComponentSpace>(TargetGraph, FVector2D(-720.0f, 0.0f));
        if (!LocalToComponentNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create LocalToComponentSpace node"));
        }
        bCreatedLocalToComponentNode = true;
    }

    bool bCreatedTrailNode = false;
    UAnimGraphNode_Trail* TrailNode = nullptr;
    for (UEdGraphNode* Node : TargetGraph->Nodes)
    {
        UAnimGraphNode_Trail* Candidate = Cast<UAnimGraphNode_Trail>(Node);
        if (Candidate && Candidate->Node.TrailBone.BoneName == TargetTrailBoneName)
        {
            TrailNode = Candidate;
            break;
        }
    }
    if (!TrailNode)
    {
        TrailNode = FindFirstNodeOfType<UAnimGraphNode_Trail>(TargetGraph);
    }
    if (!TrailNode)
    {
        TrailNode = AddAnimGraphNodeToGraph<UAnimGraphNode_Trail>(TargetGraph, FVector2D(-480.0f, 0.0f));
        if (!TrailNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create Trail node"));
        }
        bCreatedTrailNode = true;
    }

    bool bCreatedComponentToLocalNode = false;
    UAnimGraphNode_ComponentToLocalSpace* ComponentToLocalNode = FindFirstNodeOfType<UAnimGraphNode_ComponentToLocalSpace>(TargetGraph);
    if (!ComponentToLocalNode)
    {
        ComponentToLocalNode = AddAnimGraphNodeToGraph<UAnimGraphNode_ComponentToLocalSpace>(TargetGraph, FVector2D(-240.0f, 0.0f));
        if (!ComponentToLocalNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create ComponentToLocalSpace node"));
        }
        bCreatedComponentToLocalNode = true;
    }
    RootNode->NodePosX = 0.0f;
    RootNode->NodePosY = 0.0f;

    bool bSettingsChanged = false;
    TArray<FString> ChangedFields;

    if (TrailNode->Node.TrailBone.BoneName != TargetTrailBoneName)
    {
        TrailNode->Node.TrailBone.BoneName = TargetTrailBoneName;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("TrailBone"));
    }
    if (TrailNode->Node.BaseJoint.BoneName != TargetBaseJointName)
    {
        TrailNode->Node.BaseJoint.BoneName = TargetBaseJointName;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("BaseJoint"));
    }
    if (TrailNode->Node.ChainLength != ChainLength)
    {
        TrailNode->Node.ChainLength = ChainLength;
#if WITH_EDITOR
        TrailNode->Node.EnsureChainSize();
#endif
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("ChainLength"));
    }
    if (TrailNode->Node.ChainBoneAxis != ChainBoneAxis)
    {
        TrailNode->Node.ChainBoneAxis = ChainBoneAxis;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("ChainBoneAxis"));
    }
    if (TrailNode->Node.Alpha != Alpha)
    {
        TrailNode->Node.Alpha = Alpha;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("Alpha"));
    }
    if (UEdGraphPin* AlphaPin = FUnrealMCPCommonUtils::FindPin(TrailNode, TEXT("Alpha"), EGPD_Input))
    {
        const FString AlphaDefault = FString::Printf(TEXT("%f"), Alpha);
        if (!AlphaPin->DefaultValue.Equals(AlphaDefault, ESearchCase::CaseSensitive))
        {
            if (TargetGraph->GetSchema())
            {
                TargetGraph->GetSchema()->TrySetDefaultValue(*AlphaPin, AlphaDefault);
            }
            TrailNode->PinDefaultValueChanged(AlphaPin);
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("AlphaPin"));
        }
    }
    if (TrailNode->Node.RelaxationSpeedScale != RelaxationSpeedScale)
    {
        TrailNode->Node.RelaxationSpeedScale = RelaxationSpeedScale;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("RelaxationSpeedScale"));
    }
    if (!TrailNode->Node.FakeVelocity.Equals(FakeVelocity, KINDA_SMALL_NUMBER))
    {
        TrailNode->Node.FakeVelocity = FakeVelocity;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("FakeVelocity"));
    }
    if (UEdGraphPin* FakeVelocityPin = FUnrealMCPCommonUtils::FindPin(TrailNode, TEXT("FakeVelocity"), EGPD_Input))
    {
        const FString FakeVelocityDefault = FString::Printf(TEXT("%f,%f,%f"), FakeVelocity.X, FakeVelocity.Y, FakeVelocity.Z);
        if (!FakeVelocityPin->DefaultValue.Equals(FakeVelocityDefault, ESearchCase::CaseSensitive))
        {
            if (TargetGraph->GetSchema())
            {
                TargetGraph->GetSchema()->TrySetDefaultValue(*FakeVelocityPin, FakeVelocityDefault);
            }
            TrailNode->PinDefaultValueChanged(FakeVelocityPin);
            bSettingsChanged = true;
            ChangedFields.Add(TEXT("FakeVelocityPin"));
        }
    }
    if (!!TrailNode->Node.bInvertChainBoneAxis != bInvertChainBoneAxis)
    {
        TrailNode->Node.bInvertChainBoneAxis = bInvertChainBoneAxis;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("bInvertChainBoneAxis"));
    }
    if (!!TrailNode->Node.bReorientParentToChild != bReorientParentToChild)
    {
        TrailNode->Node.bReorientParentToChild = bReorientParentToChild;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("bReorientParentToChild"));
    }
    if (!!TrailNode->Node.bActorSpaceFakeVel != bActorSpaceFakeVelocity)
    {
        TrailNode->Node.bActorSpaceFakeVel = bActorSpaceFakeVelocity;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("bActorSpaceFakeVel"));
    }
    if (!!TrailNode->Node.bLimitStretch != bLimitStretch)
    {
        TrailNode->Node.bLimitStretch = bLimitStretch;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("bLimitStretch"));
    }
    if (TrailNode->Node.StretchLimit != StretchLimit)
    {
        TrailNode->Node.StretchLimit = StretchLimit;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("StretchLimit"));
    }
    if (TrailNode->Node.MaxDeltaTime != MaxDeltaTime)
    {
        TrailNode->Node.MaxDeltaTime = MaxDeltaTime;
        bSettingsChanged = true;
        ChangedFields.Add(TEXT("MaxDeltaTime"));
    }

    UEdGraphPin* InputPoseOutput = FindFirstPosePin(InputPoseNode, EGPD_Output);
    UEdGraphPin* LocalToComponentInput = FindFirstPosePin(LocalToComponentNode, EGPD_Input, { TEXT("Pose") });
    UEdGraphPin* LocalToComponentOutput = FindFirstComponentPosePin(LocalToComponentNode, EGPD_Output);
    UEdGraphPin* TrailInput = FindFirstComponentPosePin(TrailNode, EGPD_Input, { TEXT("ComponentPose") });
    UEdGraphPin* TrailOutput = FindFirstComponentPosePin(TrailNode, EGPD_Output);
    UEdGraphPin* ComponentToLocalInput = FindFirstComponentPosePin(ComponentToLocalNode, EGPD_Input, { TEXT("ComponentPose") });
    UEdGraphPin* ComponentToLocalOutput = FindFirstPosePin(ComponentToLocalNode, EGPD_Output);
    UEdGraphPin* RootInput = FindFirstPosePin(RootNode, EGPD_Input, { TEXT("Result") });

    if (!InputPoseOutput || !LocalToComponentInput || !LocalToComponentOutput || !TrailInput || !TrailOutput || !ComponentToLocalInput || !ComponentToLocalOutput || !RootInput)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve one or more required pose pins for Trail demo chain"));
    }

    bool bLinkChanged = false;
    bool bChangedThisLink = false;
    FString LinkError;
    TSharedPtr<FJsonObject> LinkErrorObj;
    if (!EnsureAnimGraphConnection(TargetGraph, InputPoseOutput, LocalToComponentInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, LocalToComponentOutput, TrailInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, TrailOutput, ComponentToLocalInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    if (!EnsureAnimGraphConnection(TargetGraph, ComponentToLocalOutput, RootInput, bReplaceExisting, bChangedThisLink, LinkError, &LinkErrorObj))
    {
        if (LinkErrorObj.IsValid())
        {
            AddGraphField(LinkErrorObj, Blueprint, TargetGraph);
            return LinkErrorObj;
        }
        return FUnrealMCPCommonUtils::CreateErrorResponse(LinkError);
    }
    bLinkChanged |= bChangedThisLink;

    const bool bGraphChanged = bCreatedInputNode || bCreatedLocalToComponentNode || bCreatedTrailNode || bCreatedComponentToLocalNode || bSettingsChanged || bLinkChanged;
    if (bGraphChanged)
    {
        FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
        TargetGraph->NotifyGraphChanged();
    }

    TArray<TSharedPtr<FJsonValue>> ChangedFieldValues;
    for (const FString& FieldName : ChangedFields)
    {
        ChangedFieldValues.Add(MakeShared<FJsonValueString>(FieldName));
    }

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetBoolField(TEXT("connected"), true);
    ResultObj->SetBoolField(TEXT("graph_changed"), bGraphChanged);
    ResultObj->SetBoolField(TEXT("created_input_node"), bCreatedInputNode);
    ResultObj->SetBoolField(TEXT("created_local_to_component_node"), bCreatedLocalToComponentNode);
    ResultObj->SetBoolField(TEXT("created_trail_node"), bCreatedTrailNode);
    ResultObj->SetBoolField(TEXT("created_component_to_local_node"), bCreatedComponentToLocalNode);
    ResultObj->SetBoolField(TEXT("settings_changed"), bSettingsChanged);
    ResultObj->SetBoolField(TEXT("links_changed"), bLinkChanged);
    ResultObj->SetStringField(TEXT("trail_bone"), TrailBoneName);
    ResultObj->SetStringField(TEXT("base_joint"), BaseJointName);
    ResultObj->SetNumberField(TEXT("chain_length"), ChainLength);
    ResultObj->SetStringField(TEXT("chain_bone_axis"), GetTrailChainBoneAxisName(ChainBoneAxis));
    ResultObj->SetNumberField(TEXT("alpha"), Alpha);
    ResultObj->SetStringField(TEXT("fake_velocity"), FakeVelocity.ToString());
    ResultObj->SetBoolField(TEXT("actor_space_fake_velocity"), bActorSpaceFakeVelocity);
    ResultObj->SetBoolField(TEXT("reorient_parent_to_child"), bReorientParentToChild);
    ResultObj->SetArrayField(TEXT("changed_fields"), ChangedFieldValues);
    ResultObj->SetObjectField(TEXT("input_pose_node"), NodeToJson(InputPoseNode, true));
    ResultObj->SetObjectField(TEXT("local_to_component_node"), NodeToJson(LocalToComponentNode, true));
    ResultObj->SetObjectField(TEXT("trail_node"), NodeToJson(TrailNode, true));
    ResultObj->SetObjectField(TEXT("component_to_local_node"), NodeToJson(ComponentToLocalNode, true));
    ResultObj->SetObjectField(TEXT("root_node"), NodeToJson(RootNode, true));
    ResultObj->SetObjectField(TEXT("settings"), AnimGraphNodeSettingsToJson(TrailNode, 4));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintInputAxisEventNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString AxisName;
    if (!Params->TryGetStringField(TEXT("axis_name"), AxisName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'axis_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_InputAxisEvent* AxisNode = NewObject<UK2Node_InputAxisEvent>(TargetGraph);
    if (!AxisNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create input axis event node"));
    }

    AxisNode->Initialize(FName(*AxisName));
    AxisNode->NodePosX = NodePosition.X;
    AxisNode->NodePosY = NodePosition.Y;
    if (Params->HasField(TEXT("consume_input")))
    {
        AxisNode->bConsumeInput = Params->GetBoolField(TEXT("consume_input"));
    }
    if (Params->HasField(TEXT("execute_when_paused")))
    {
        AxisNode->bExecuteWhenPaused = Params->GetBoolField(TEXT("execute_when_paused"));
    }
    if (Params->HasField(TEXT("override_parent_binding")))
    {
        AxisNode->bOverrideParentBinding = Params->GetBoolField(TEXT("override_parent_binding"));
    }

    TargetGraph->AddNode(AxisNode, true);
    AxisNode->CreateNewGuid();
    AxisNode->PostPlacedNewNode();
    AxisNode->AllocateDefaultPins();
    AxisNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(AxisNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEnhancedInputActionNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString InputActionPath;
    if (!Params->TryGetStringField(TEXT("input_action"), InputActionPath))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'input_action' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UInputAction* InputAction = Cast<UInputAction>(LoadObjectForPin(InputActionPath));
    if (!InputAction)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("InputAction not found: %s"), *InputActionPath));
    }

    UK2Node_EnhancedInputAction* InputActionNode = NewObject<UK2Node_EnhancedInputAction>(TargetGraph);
    if (!InputActionNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create enhanced input action node"));
    }

    InputActionNode->InputAction = InputAction;
    InputActionNode->NodePosX = NodePosition.X;
    InputActionNode->NodePosY = NodePosition.Y;
    TargetGraph->AddNode(InputActionNode, true);
    InputActionNode->CreateNewGuid();
    InputActionNode->PostPlacedNewNode();
    InputActionNode->AllocateDefaultPins();
    InputActionNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(InputActionNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintVariableGetNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString VariableName;
    if (!Params->TryGetStringField(TEXT("variable_name"), VariableName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_VariableGet* VariableGetNode = nullptr;
    FString TargetClassName;
    if (Params->TryGetStringField(TEXT("target_class"), TargetClassName) && !TargetClassName.IsEmpty())
    {
        UClass* TargetClass = LoadClassForPin(TargetClassName);
        if (!TargetClass || !TargetClass->IsChildOf(UObject::StaticClass()))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Target class not found or not a UObject class: %s"), *TargetClassName));
        }

        FProperty* Property = FindFProperty<FProperty>(TargetClass, FName(*VariableName));
        if (!Property)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Variable not found on target class %s: %s"), *TargetClass->GetName(), *VariableName));
        }

        VariableGetNode = NewObject<UK2Node_VariableGet>(TargetGraph);
        if (!VariableGetNode)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create variable get node"));
        }

        VariableGetNode->VariableReference.SetFromField<FProperty>(Property, false);
        VariableGetNode->NodePosX = NodePosition.X;
        VariableGetNode->NodePosY = NodePosition.Y;
        TargetGraph->AddNode(VariableGetNode, true);
        VariableGetNode->CreateNewGuid();
        VariableGetNode->PostPlacedNewNode();
        VariableGetNode->AllocateDefaultPins();
    }
    else
    {
        VariableGetNode = FUnrealMCPCommonUtils::CreateVariableGetNode(TargetGraph, Blueprint, VariableName, NodePosition);
    }

    if (!VariableGetNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Variable not found: %s"), *VariableName));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(VariableGetNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintVariableSetNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString VariableName;
    if (!Params->TryGetStringField(TEXT("variable_name"), VariableName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'variable_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_VariableSet* VariableSetNode = FUnrealMCPCommonUtils::CreateVariableSetNode(TargetGraph, Blueprint, VariableName, NodePosition);
    if (!VariableSetNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Variable not found: %s"), *VariableName));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(VariableSetNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintMathNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString Operation;
    if (!Params->TryGetStringField(TEXT("operation"), Operation))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'operation' parameter"));
    }

    const FName FunctionName = GetMathFunctionName(Operation);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Unsupported math operation: %s"), *Operation));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UFunction* Function = UKismetMathLibrary::StaticClass()->FindFunctionByName(FunctionName);
    if (!Function)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Math function not found: %s"), *FunctionName.ToString()));
    }

    UK2Node_CallFunction* MathNode = FUnrealMCPCommonUtils::CreateFunctionCallNode(TargetGraph, Function, NodePosition);
    if (!MathNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create math node"));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(MathNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintCompareNode(const TSharedPtr<FJsonObject>& Params)
{
    FString Operation;
    if (!Params->TryGetStringField(TEXT("operation"), Operation))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'operation' parameter"));
    }

    FString ValueType = TEXT("double");
    Params->TryGetStringField(TEXT("value_type"), ValueType);

    FString MappingError;
    const FName FunctionName = GetCompareFunctionName(Operation, ValueType, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    return CreateBlueprintFunctionLibraryNode(Params, UKismetMathLibrary::StaticClass(), FunctionName, TEXT("compare"));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintBooleanNode(const TSharedPtr<FJsonObject>& Params)
{
    FString Operation;
    if (!Params->TryGetStringField(TEXT("operation"), Operation))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'operation' parameter"));
    }

    FString MappingError;
    const FName FunctionName = GetBooleanFunctionName(Operation, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    return CreateBlueprintFunctionLibraryNode(Params, UKismetMathLibrary::StaticClass(), FunctionName, TEXT("boolean"));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintSelectNode(const TSharedPtr<FJsonObject>& Params)
{
    FString ValueType = TEXT("int");
    Params->TryGetStringField(TEXT("value_type"), ValueType);

    FString MappingError;
    const FName FunctionName = GetSelectFunctionName(ValueType, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    return CreateBlueprintFunctionLibraryNode(Params, UKismetMathLibrary::StaticClass(), FunctionName, TEXT("select"));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintLiteralNode(const TSharedPtr<FJsonObject>& Params)
{
    FString LiteralType;
    if (!Params->TryGetStringField(TEXT("literal_type"), LiteralType) && !Params->TryGetStringField(TEXT("value_type"), LiteralType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'literal_type' parameter"));
    }

    FString MappingError;
    const FName FunctionName = GetLiteralFunctionName(LiteralType, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UFunction* Function = UKismetSystemLibrary::StaticClass()->FindFunctionByName(FunctionName);
    if (!Function)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Literal function not found: %s"), *FunctionName.ToString()));
    }

    UK2Node_CallFunction* LiteralNode = FUnrealMCPCommonUtils::CreateFunctionCallNode(TargetGraph, Function, NodePosition);
    if (!LiteralNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create literal node"));
    }

    const TSharedPtr<FJsonValue> LiteralValue = Params->TryGetField(TEXT("value"));
    if (LiteralValue.IsValid())
    {
        UEdGraphPin* ValuePin = FUnrealMCPCommonUtils::FindPin(LiteralNode, TEXT("Value"), EGPD_Input);
        const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
        if (!ValuePin || !K2Schema)
        {
            LiteralNode->DestroyNode();
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve literal value pin"));
        }

        FString RequestedDefaultValue;
        FString DefaultResolveError;
        if (!GetPinDefaultStringForTypeChecked(LiteralValue, ValuePin->PinType, RequestedDefaultValue, DefaultResolveError))
        {
            LiteralNode->DestroyNode();
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid literal value for type '%s': %s"), *LiteralType, *DefaultResolveError));
        }
        K2Schema->TrySetDefaultValue(*ValuePin, RequestedDefaultValue);
        const FString DefaultError = K2Schema->IsCurrentPinDefaultValid(ValuePin);
        if (!DefaultError.IsEmpty() || !K2Schema->DoesDefaultValueMatch(*ValuePin, RequestedDefaultValue))
        {
            LiteralNode->DestroyNode();
            const FString EffectiveError = DefaultError.IsEmpty()
                ? FString::Printf(TEXT("Requested default was not accepted. requested='%s'"), *RequestedDefaultValue)
                : DefaultError;
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid literal value for type '%s': %s"), *LiteralType, *EffectiveError));
        }

        LiteralNode->PinDefaultValueChanged(ValuePin);
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);
    TSharedPtr<FJsonObject> ResultObj = NodeToJson(LiteralNode, true);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintEnumLiteralNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    const FString EnumType = GetEnumTypeParam(Params);
    if (EnumType.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing enum type parameter. Use 'enum_type', 'type_object', or 'enum_path'"));
    }

    UEnum* Enum = LoadEnumForPin(EnumType);
    if (!Enum)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Enum not found: %s"), *EnumType));
    }

    FString DefaultValue;
    int32 EnumIndex = INDEX_NONE;
    FString DefaultError;
    if (!ResolveEnumValueDefaultString(Params->TryGetField(TEXT("value")), Enum, DefaultValue, EnumIndex, DefaultError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid enum literal value: %s"), *DefaultError));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    UK2Node_EnumLiteral* EnumLiteralNode = NewObject<UK2Node_EnumLiteral>(TargetGraph);
    if (!EnumLiteralNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create enum literal node"));
    }

    EnumLiteralNode->Enum = Enum;
    EnumLiteralNode->NodePosX = NodePosition.X;
    EnumLiteralNode->NodePosY = NodePosition.Y;

    TargetGraph->AddNode(EnumLiteralNode, true);
    EnumLiteralNode->CreateNewGuid();
    EnumLiteralNode->PostPlacedNewNode();
    EnumLiteralNode->AllocateDefaultPins();
    EnumLiteralNode->ReconstructNode();

    UEdGraphPin* EnumInputPin = FUnrealMCPCommonUtils::FindPin(EnumLiteralNode, UK2Node_EnumLiteral::GetEnumInputPinName().ToString(), EGPD_Input);
    if (!EnumInputPin)
    {
        EnumLiteralNode->DestroyNode();
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to resolve enum literal input pin"));
    }

    K2Schema->TrySetDefaultValue(*EnumInputPin, DefaultValue);
    const FString AppliedDefaultError = K2Schema->IsCurrentPinDefaultValid(EnumInputPin);
    const int32 AppliedEnumIndex = Enum->GetIndexByNameString(EnumInputPin->DefaultValue);
    if (!AppliedDefaultError.IsEmpty() || AppliedEnumIndex != EnumIndex)
    {
        EnumLiteralNode->DestroyNode();
        const FString EffectiveError = AppliedDefaultError.IsEmpty()
            ? FString::Printf(TEXT("Requested enum literal default was not accepted. requested='%s', actual='%s'"), *DefaultValue, *EnumInputPin->DefaultValue)
            : AppliedDefaultError;
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid enum literal value: %s"), *EffectiveError));
    }

    EnumLiteralNode->PinDefaultValueChanged(EnumInputPin);
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(EnumLiteralNode, true);
    ResultObj->SetStringField(TEXT("enum_type"), Enum->GetPathName());
    ResultObj->SetStringField(TEXT("default_value"), DefaultValue);
    ResultObj->SetNumberField(TEXT("default_index"), EnumIndex);
    ResultObj->SetArrayField(TEXT("enum_entries"), EnumEntriesToJson(Enum));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintIsValidNode(const TSharedPtr<FJsonObject>& Params)
{
    FString ValueType = TEXT("object");
    Params->TryGetStringField(TEXT("value_type"), ValueType);

    FString MappingError;
    const FName FunctionName = GetIsValidFunctionName(ValueType, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    return CreateBlueprintFunctionLibraryNode(Params, UKismetSystemLibrary::StaticClass(), FunctionName, TEXT("is_valid"));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintMakeStructNode(const TSharedPtr<FJsonObject>& Params)
{
    FString StructType;
    if (!Params->TryGetStringField(TEXT("struct_type"), StructType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'struct_type' parameter"));
    }

    FString MappingError;
    const FName FunctionName = GetStructHelperFunctionName(TEXT("make"), StructType, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    return CreateBlueprintFunctionLibraryNode(Params, UKismetMathLibrary::StaticClass(), FunctionName, TEXT("make_struct"));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintBreakStructNode(const TSharedPtr<FJsonObject>& Params)
{
    FString StructType;
    if (!Params->TryGetStringField(TEXT("struct_type"), StructType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'struct_type' parameter"));
    }

    FString MappingError;
    const FName FunctionName = GetStructHelperFunctionName(TEXT("break"), StructType, MappingError);
    if (FunctionName == NAME_None)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(MappingError);
    }

    return CreateBlueprintFunctionLibraryNode(Params, UKismetMathLibrary::StaticClass(), FunctionName, TEXT("break_struct"));
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintSwitchIntNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    int32 StartIndex = 0;
    int32 CaseCount = 0;
    FString CaseError;
    if (!ResolveSwitchIntCases(Params, StartIndex, CaseCount, CaseError))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(CaseError);
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    const bool bHasDefaultPin = GetBoolParam(Params, TEXT("has_default_pin"), true);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_SwitchInteger* SwitchNode = NewObject<UK2Node_SwitchInteger>(TargetGraph);
    if (!SwitchNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create switch int node"));
    }

    SwitchNode->StartIndex = StartIndex;
    SwitchNode->bHasDefaultPin = bHasDefaultPin;
    SwitchNode->NodePosX = NodePosition.X;
    SwitchNode->NodePosY = NodePosition.Y;

    TargetGraph->AddNode(SwitchNode, true);
    SwitchNode->CreateNewGuid();
    SwitchNode->PostPlacedNewNode();
    SwitchNode->AllocateDefaultPins();

    for (int32 CaseIndex = 0; CaseIndex < CaseCount; ++CaseIndex)
    {
        SwitchNode->AddPinToSwitchNode();
    }

    SwitchNode->ReconstructNode();
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(SwitchNode, true);
    ResultObj->SetNumberField(TEXT("start_index"), StartIndex);
    ResultObj->SetNumberField(TEXT("case_count"), CaseCount);
    ResultObj->SetBoolField(TEXT("has_default_pin"), bHasDefaultPin);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleAddBlueprintSwitchEnumNode(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    const FString EnumType = GetEnumTypeParam(Params);
    if (EnumType.IsEmpty())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing enum type parameter. Use 'enum_type', 'type_object', or 'enum_path'"));
    }

    UEnum* Enum = LoadEnumForPin(EnumType);
    if (!Enum)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Enum not found: %s"), *EnumType));
    }

    const TArray<TSharedPtr<FJsonValue>> EnumCaseEntries = EnumEntriesToJson(Enum, true);
    if (EnumCaseEntries.Num() == 0)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Enum has no switchable values: %s"), *Enum->GetPathName()));
    }

    FVector2D NodePosition(0.0f, 0.0f);
    if (Params->HasField(TEXT("node_position")))
    {
        NodePosition = FUnrealMCPCommonUtils::GetVector2DFromJson(Params, TEXT("node_position"));
    }

    const bool bHasDefaultPin = GetBoolParam(Params, TEXT("has_default_pin"), false);

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UK2Node_SwitchEnum* SwitchNode = NewObject<UK2Node_SwitchEnum>(TargetGraph);
    if (!SwitchNode)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to create switch enum node"));
    }

    SwitchNode->SetEnum(Enum);
    SwitchNode->bHasDefaultPin = bHasDefaultPin;
    SwitchNode->NodePosX = NodePosition.X;
    SwitchNode->NodePosY = NodePosition.Y;

    TargetGraph->AddNode(SwitchNode, true);
    SwitchNode->CreateNewGuid();
    SwitchNode->PostPlacedNewNode();
    SwitchNode->AllocateDefaultPins();
    SwitchNode->ReconstructNode();

    int32 CasePinCount = 0;
    for (const UEdGraphPin* Pin : SwitchNode->Pins)
    {
        if (Pin && Pin->Direction == EGPD_Output && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Exec && Pin->PinName != FName(TEXT("Default")))
        {
            ++CasePinCount;
        }
    }

    if (CasePinCount != EnumCaseEntries.Num())
    {
        SwitchNode->DestroyNode();
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(
            TEXT("Switch enum case pin count mismatch for %s. expected=%d actual=%d"),
            *Enum->GetPathName(),
            EnumCaseEntries.Num(),
            CasePinCount));
    }

    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = NodeToJson(SwitchNode, true);
    ResultObj->SetStringField(TEXT("enum_type"), Enum->GetPathName());
    ResultObj->SetNumberField(TEXT("case_count"), CasePinCount);
    ResultObj->SetBoolField(TEXT("has_default_pin"), bHasDefaultPin);
    ResultObj->SetArrayField(TEXT("enum_entries"), EnumCaseEntries);
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleSetBlueprintPinDefault(const TSharedPtr<FJsonObject>& Params)
{
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString NodeId;
    if (!Params->TryGetStringField(TEXT("node_id"), NodeId))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'node_id' parameter"));
    }

    FString PinName;
    if (!Params->TryGetStringField(TEXT("pin_name"), PinName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'pin_name' parameter"));
    }

    TSharedPtr<FJsonValue> Value = Params->TryGetField(TEXT("value"));
    if (!Value.IsValid())
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'value' parameter"));
    }

    FString Direction;
    Params->TryGetStringField(TEXT("direction"), Direction);

    EEdGraphPinDirection PinDirection = EGPD_MAX;
    if (Direction.Equals(TEXT("input"), ESearchCase::IgnoreCase))
    {
        PinDirection = EGPD_Input;
    }
    else if (Direction.Equals(TEXT("output"), ESearchCase::IgnoreCase))
    {
        PinDirection = EGPD_Output;
    }

    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    UEdGraphNode* Node = FindNodeById(TargetGraph, NodeId);
    if (!Node)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Node not found: %s"), *NodeId));
    }

    UEdGraphPin* Pin = FUnrealMCPCommonUtils::FindPin(Node, PinName, PinDirection);
    if (!Pin)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Pin not found: %s"), *PinName));
    }

    const UEdGraphSchema_K2* K2Schema = Cast<const UEdGraphSchema_K2>(TargetGraph->GetSchema());
    if (!K2Schema)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Failed to get K2 schema"));
    }

    const FString PreviousDefaultValue = Pin->DefaultValue;
    UObject* PreviousDefaultObject = Pin->DefaultObject;
    const FText PreviousDefaultTextValue = Pin->DefaultTextValue;
    FString RequestedDefaultValue;
    UObject* RequestedDefaultObject = nullptr;
    bool bRequestedDefaultValue = false;
    bool bRequestedDefaultObject = false;

    if (Value->Type == EJson::String && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Class)
    {
        UClass* Class = LoadClassForPin(Value->AsString());
        if (!Class)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Class not found: %s"), *Value->AsString()));
        }
        RequestedDefaultObject = Class;
        bRequestedDefaultObject = true;
        K2Schema->TrySetDefaultObject(*Pin, Class);
    }
    else if (Value->Type == EJson::String && Pin->PinType.PinCategory == UEdGraphSchema_K2::PC_Object)
    {
        UObject* Object = LoadObjectForPin(Value->AsString());
        if (!Object)
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Object not found: %s"), *Value->AsString()));
        }
        RequestedDefaultObject = Object;
        bRequestedDefaultObject = true;
        K2Schema->TrySetDefaultObject(*Pin, Object);
    }
    else
    {
        FString DefaultResolveError;
        if (!GetPinDefaultStringForTypeChecked(Value, Pin->PinType, RequestedDefaultValue, DefaultResolveError))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for pin '%s': %s"), *PinName, *DefaultResolveError));
        }
        bRequestedDefaultValue = true;
        K2Schema->TrySetDefaultValue(*Pin, RequestedDefaultValue);
    }

    const FString DefaultError = K2Schema->IsCurrentPinDefaultValid(Pin);
    const bool bDefaultValueApplied = !bRequestedDefaultValue || K2Schema->DoesDefaultValueMatch(*Pin, RequestedDefaultValue);
    const bool bDefaultObjectApplied = !bRequestedDefaultObject || Pin->DefaultObject == RequestedDefaultObject;
    if (!DefaultError.IsEmpty() || !bDefaultValueApplied || !bDefaultObjectApplied)
    {
        Pin->DefaultValue = PreviousDefaultValue;
        Pin->DefaultObject = PreviousDefaultObject;
        Pin->DefaultTextValue = PreviousDefaultTextValue;
        const FString EffectiveError = DefaultError.IsEmpty()
            ? FString::Printf(TEXT("Requested default was not accepted. requested='%s', actual='%s'"), *RequestedDefaultValue, *Pin->GetDefaultAsString())
            : DefaultError;
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Invalid default value for pin '%s': %s"), *PinName, *EffectiveError));
    }

    Node->PinDefaultValueChanged(Pin);
    FBlueprintEditorUtils::MarkBlueprintAsModified(Blueprint);

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetStringField(TEXT("node_id"), NodeId);
    ResultObj->SetObjectField(TEXT("pin"), PinToJson(Pin));
    AddGraphField(ResultObj, Blueprint, TargetGraph);
    return ResultObj;
}

TSharedPtr<FJsonObject> FUnrealMCPBlueprintNodeCommands::HandleFindBlueprintNodes(const TSharedPtr<FJsonObject>& Params)
{
    // Get required parameters
    FString BlueprintName;
    if (!Params->TryGetStringField(TEXT("blueprint_name"), BlueprintName))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'blueprint_name' parameter"));
    }

    FString NodeType;
    if (!Params->TryGetStringField(TEXT("node_type"), NodeType))
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'node_type' parameter"));
    }

    // Find the blueprint
    UBlueprint* Blueprint = FUnrealMCPCommonUtils::FindBlueprint(BlueprintName);
    if (!Blueprint)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(FString::Printf(TEXT("Blueprint not found: %s"), *BlueprintName));
    }

    FString GraphError;
    UEdGraph* TargetGraph = ResolveBlueprintGraphForNodeCommand(Blueprint, Params, GraphError);
    if (!TargetGraph)
    {
        return FUnrealMCPCommonUtils::CreateErrorResponse(GraphError);
    }

    // Create a JSON array for the node GUIDs
    TArray<TSharedPtr<FJsonValue>> NodeGuidArray;

    // Filter nodes by the exact requested type
    if (NodeType == TEXT("Event"))
    {
        FString EventName;
        if (!Params->TryGetStringField(TEXT("event_name"), EventName))
        {
            return FUnrealMCPCommonUtils::CreateErrorResponse(TEXT("Missing 'event_name' parameter for Event node search"));
        }

        // Look for nodes with exact event name (e.g., ReceiveBeginPlay)
        for (UEdGraphNode* Node : TargetGraph->Nodes)
        {
            UK2Node_Event* EventNode = Cast<UK2Node_Event>(Node);
            if (EventNode && EventNode->EventReference.GetMemberName() == FName(*EventName))
            {
                UE_LOG(LogTemp, Display, TEXT("Found event node with name %s: %s"), *EventName, *EventNode->NodeGuid.ToString());
                NodeGuidArray.Add(MakeShared<FJsonValueString>(EventNode->NodeGuid.ToString()));
            }
        }
    }
    // Add other node types as needed (InputAction, etc.)

    TSharedPtr<FJsonObject> ResultObj = MakeShared<FJsonObject>();
    ResultObj->SetArrayField(TEXT("node_guids"), NodeGuidArray);
    AddGraphField(ResultObj, Blueprint, TargetGraph);

    return ResultObj;
}
